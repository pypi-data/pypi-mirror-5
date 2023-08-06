"""ResourceSync explorer

This is the guts of a client designed to 'explore' the ResourceSync
facilities offered by a source. Will use standard practices to 
look for and interpret capabilities.
"""

import sys
import urllib
import urlparse
import os.path
import datetime
import distutils.dir_util 
import re
import time
import logging
import requests

from resync.mapper import Mapper
from resync.sitemap import Sitemap
from resync.client import Client,ClientFatalError
from resync.client_state import ClientState
from w3c_datetime import str_to_datetime,datetime_to_str

class XResource(object):
    """Information about a resource for the explorer

    Must have a uri but may also store:
    
    acceptable_capabilities - None for any acceptable, 'resource' if a 
        resource rather than a capability document is expected, else 
        a list of capability names
    checks - a set of information to check when then XResource is inspected
    base_uri - on creation interpret any relative URI specified in the 
        context of base_uri, store the resulting full URI
    """
    def __init__(self, uri, acceptable_capabilities=None, checks=None, context=None):
        self.uri=urlparse.urljoin(context,uri)
        self.acceptable_capabilities=acceptable_capabilities
        self.checks=checks

class HeadResponse(object):
    """Object to mock up requests.head(...) response"""
    def __init__(self):
        self.status_code=None
        self.headers={}

class ExplorerQuit(Exception):
    """Exception raised when user quits normally, no error"""
    pass

class Explorer(Client):
    """Extension of the client code to explore a ResourceSync source

    Designed to support a text-based command-line client that starts from
    a given URI, server, or local file, and then allows interactive 
    exploration of ResourceSync capabilities offered by the source.
    """

    def explore(self):
        """INTERACTIVE exploration source capabilities
        
        Will use sitemap URI taken either from explicit self.sitemap_name
        or derived from the mappings supplied.
        """
        # Where do we start? Build options in starts which has entries
        # that are a pair comprised of the uri and a list of acceptable
        # capabilities
        starts = []
        if (self.sitemap_name is not None):
            print "Starting from explicit --sitemap %s" % (uri)
            starts.append( XResource(uri) )
        elif (len(self.mapper)>0):
            uri = self.mapper.default_src_uri()
            (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(uri)
            if (not scheme and not netloc):
                if (os.path.isdir(path)):
                    # have a dir, look for 'likely' file names
                    print "Looking for capability documents in local directory %s" % (path)
                    for name in ['resourcesync','capabilities.xml',
                                 'resourcelist.xml','changelist.xml']:
                        file = os.path.join(path,name)
                        if (os.path.isfile(file)):
                            starts.append( XResource(file) )
                    if (len(starts)==0):
                        raise ClientFatalError( "No likely capability files found in local directory %s" %
                                                (path) )
                else:
                    # local file, might be anything (or not exist)
                    print "Starting from local file %s" % (path)
                    starts.append( XResource(path) )
            else:
                # remote, can't tell whether we have a sitemap or a server name or something 
                # else, build list of options depending on whether there is a path and whether
                # there is an extension/name
                well_known = urlparse.urlunparse( [ scheme,netloc,'/.well-known/resourcesync','','','' ] )
                if (not path):
                    # root, just look for .well-known
                    starts.append( XResource(well_known, ['capabilitylist','capabilitylistindex']) )
                else:
                    starts.append( XResource(uri) )
                    starts.append( XResource(well_known, ['capabilitylist','capabilitylistindex']) )
                print "Looking for discovery information based on mappings"
        else:
            raise ClientFatalError("No source information (server base uri or capability uri) specified, use -h for help")
        # 
        # Have list of one or more possible starting point, try them in turn
        try:
            for start in starts:
                # For each starting point we create a fresh history
                history = [ start ]
                input = None
                while (len(history)>0):
                    print
                    xr = history.pop()
                    new_xr = self.explore_uri(xr,len(history)>0)
                    if (new_xr):
                        # Add current and new to history
                        history.append( xr )
                        history.append( new_xr )
        except ExplorerQuit:
            pass # expected way to exit
        print "\nresync-explorer done, bye...\n"

    def explore_uri(self, explorer_resource, show_back=True):
        """INTERACTIVE exploration of capabilities document(s) starting at a given URI

        Will flag warnings if the document is not of type listed in caps
        """
        uri = explorer_resource.uri
        caps = explorer_resource.acceptable_capabilities
        checks = explorer_resource.checks
        print "Reading %s" % (uri)
        options={}
        capability=None
        try:
            if (caps=='resource'):
                # Not expecting a capability document
                self.explore_show_head(uri,check_headers=checks)
            else: 
                s=Sitemap()
                list = s.parse_xml(urllib.urlopen(uri))
                (options,capability)=self.explore_show_summary(list,s.parsed_index,caps,context=uri)
        except IOError as e:
            print "Cannot read %s (%s)\nGoing back" % (uri,str(e))
            return(None)
        except Exception as e:
            print "Cannot parse %s (%s)\nGoing back" % (uri,str(e))
            return(None)
        #
        # Loop until we have some valide input
        #
        while (True):
            # don't offer number option for no resources/capabilities
            num_prompt = '' if (len(options)==0) else 'number, '
            up_prompt = 'b(ack), ' if (show_back) else ''
            input = raw_input( "Follow [%s%sq(uit)]?" % (num_prompt,up_prompt) )
            if (input in options.keys()):
                break
            if (input == 'q'):
                raise ExplorerQuit()
            if (input == 'b'):
                return(None)
        #
        # Got input that is one of the options
        #
        checks = {}
        r = options[input]
        if ( r.capability is None ):
            if (capability == 'capabilitylistindex'):
                # all links should be to capabilitylist documents
                caps = ['capabilitylist']
            elif (capability in ['resourcelist','changelist',
                                 'resourcedump','changedump']):
                caps = 'resource'
        else:
            caps = [r.capability]
        # Record anything we know about the resource to check
        if (r.length is not None):
            checks['content-length']=r.length
        if (r.lastmod is not None):
            checks['last-modified']=r.lastmod
        # FIXME - could do sanity check here and issue warnings if odd
        return( XResource(options[input].uri, caps, checks) )

    def explore_show_summary(self, list, index=False, expected=None, context=None):
        """Show summary of one capability document

        Given a capability document or index (in list, index True if it is an 
        index), write out a simply textual summary of the document with all 
        related documents shown as numbered options (of the form 
        [#] ...description...) which will then form a menu for the next 
        exploration.

        If expected is not None then it should be a list of expected document
        types. If this is set then a warning will be printed if list is not
        one of these document types.

        FIXME - should look for <rs:ln rel="up"...> link and show that
        """
        num_entries = len(list.resources)
        capability = '(unknown capability)'
        if ('capability' in list.md):
            capability = list.md['capability']
        if (index):
            capability += 'index'
        print "Parsed %s document with %d entries:" % (capability,num_entries)
        if (expected is not None and capability not in expected):
            print "WARNING - expected a %s document" % (','.join(expected))
        to_show = num_entries
        if (num_entries>21):
            to_show = 20
        # What entries are allowed? 
        # FIXME - not complete
        entry_caps = []
        if (capability == 'capabilitylistindex'):
            entry_caps = ['capabilitylist']
        elif (capability == 'capabilitylist'):
            entry_caps = ['resourcelist','changelist','resourcedump','changedump','changelistindex']
        elif (capability == 'changelistindex'):
            entry_caps = ['changelist']
        options = {}
        n=0
        # Look for <rs:ln> elements in this document
        if ('resourcesync' in list.ln):
            options['rs']=list.ln['resourcesync']
            print "[%s] %s" % ('rs',list.ln['resourcesync'].uri)
        if ('up' in list.ln):
            options['up']=list.ln['up']
            print "[%s] %s" % ('up',list.ln['up'].uri)
        if ('db' in list.ln):
            options['db']=list.ln['describedby']
            print "[%s] %s" % ('db',list.ln['describedby'].uri)
        # Show listed resources as numbered options
        for r in list.resources:
            if (n>=to_show):
                print "(not showing remaining %d entries)" % (num_entries-n)
                break
            n+=1
            options[str(n)]=r
            print "[%d] %s" % (n,r.uri)
            if (self.verbose):
                print "  " + str(r)
            full_uri = urlparse.urljoin(context,r.uri)
            if (full_uri != r.uri):
                print "  WARNING - expanded relative URI to %s" % (full_uri)
                r.uri = full_uri
            if (r.capability is not None):
                warning = ''
                if (r.capability not in entry_caps):
                    warning = " (EXPECTED %s)" % (' or '.join(entry_caps))
                print "  %s%s" % (r.capability,warning)
            elif (len(entry_caps)==1):
                r.capability=entry_caps[0]
                print "  capability not specified, should be %s" % (r.capability)
        return(options,capability)

    def explore_show_head(self,uri,check_headers=None):
        """Do HEAD on uri and show infomation

        Will also check headers against any values specified in 
        check_headers.
        """
        print "HEAD %s" % (uri)
        if (re.match(r'^\w+:', uri)):
            # Looks like a URI
            response = requests.head(uri)
        else:
            # Mock up response if we have a local file
            response = self.head_on_file(uri)
        print "  status: %s" % (response.status_code)
        if (response.status_code=='200'):
            # generate normalized lastmod
#        if ('last-modified' in response.headers):
#            response.headers.add['lastmod'] = datetime_to_str(str_to_datetime(response.headers['last-modified']))
        # print some of the headers
            for header in ['content-length','last-modified','lastmod','content-type','etag']:
                if header in response.headers:
                    check_str=''
                    if (check_headers is not None and
                        header in check_headers):
                        if (response.headers[header] == check_headers[header]):
                            check_str=' MATCHES EXPECTED VALUE'
                        else:
                            check_str=' EXPECTED %s' % (check_headers[header])
                    print "  %s: %s%s" % (header, response.headers[header], check_str)

    def head_on_file(self,file):
        """Mock up requests.head(..) response on local file
        """
        response = HeadResponse()
        if (not os.path.isfile(file)):
            response.status_code='404'
        else:
            response.status_code='200'
            response.headers['last-modified']=datetime_to_str(os.path.getmtime(file))
            response.headers['content-length']=os.path.getsize(file)
        return(response)
