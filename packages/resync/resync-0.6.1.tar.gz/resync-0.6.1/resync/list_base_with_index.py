"""Base class for ResourceSync capabilities with lists of resources including 
support for both sitemaps and sitemapindexes.

Extends ListBase to add support for sitemapindexes.
"""

import collections
import os
from datetime import datetime
import re
import sys
from urllib import URLopener

from list_base import ListBase
from resource import Resource
from sitemap import Sitemap
from mapper import Mapper, MapperError
from url_authority import UrlAuthority
from utils import compute_md5_for_file

class ListBaseIndexError(Exception):
    """Exception for problems with sitemapindexes"""
    pass

class ListBaseWithIndex(ListBase):

    def __init__(self, resources=None, md=None, ln=None, allow_multifile=None, mapper=None):
        super(ListBaseWithIndex, self).__init__(resources=resources, md=md, ln=ln)
        # specific to lists with indexes
        self.resources_class=dict
        self.max_sitemap_entries=50000
        self.mapper = mapper
        self.allow_multifile = (True if (allow_multifile is None) else allow_multifile)
        self.check_url_authority = False
        self.content_length = 0
        self.num_files = 0            # Number of files read
        self.bytes_read = 0           # Aggregate of content_length values

    ##### INPUT #####

    def read(self, uri=None, resources=None, capability=None, index_only=False):
        """Read sitemap from a URI including handling sitemapindexes

        If index_only is True then individual sitemaps references in a sitemapindex
        will not be read. This will result in no resources being returned and is
        useful only to read the metadata and links listed in the sitemapindex.

        Includes the subtlety that if the input URI is a local file and is a 
        sitemapindex which contains URIs for the individual sitemaps, then these
        are mapped to the filesystem also.
        """
        try:
            fh = URLopener().open(uri)
            self.num_files += 1
        except IOError as e:
            raise IOError("Failed to load sitemap/sitemapindex from %s (%s)" % (uri,str(e)))
        # Get the Content-Length if we can (works fine for local files)
        try:
            self.content_length = int(fh.info()['Content-Length'])
            self.bytes_read += self.content_length
            self.logger.debug( "Read %d bytes from %s" % (self.content_length,uri) )
        except KeyError:
            # If we don't get a length then c'est la vie
            self.logger.debug( "Read ????? bytes from %s" % (uri) )
            pass
        self.logger.info( "Read sitemap/sitemapindex from %s" % (uri) )
        s = self.new_sitemap()
        s.parse_xml(fh=fh,resources=self,capability='resourcelist')
        # what did we read? sitemap or sitemapindex?
        if (s.parsed_index):
            # sitemapindex
            if (not self.allow_multifile):
                raise ListBaseIndexError("Got sitemapindex from %s but support for sitemapindex disabled" % (uri))
            self.logger.info( "Parsed as sitemapindex, %d sitemaps" % (len(self.resources)) )
            sitemapindex_is_file = self.is_file_uri(uri)
            if (index_only):
                # don't read the component sitemaps
                self.sitemapindex = True
                return
            # now loop over all entries to read each sitemap and add to resources
            sitemaps = self.resources
            self.resources = self.resources_class()
            self.logger.info( "Now reading %d sitemaps" % len(sitemaps.uris()) )
            for sitemap_uri in sorted(sitemaps.uris()):
                self.read_component_sitemap(uri,sitemap_uri,s,sitemapindex_is_file)
        else:
            # sitemap
            self.logger.info( "Parsed as sitemap, %d resources" % (len(self.resources)) )


    def read_component_sitemap(self, sitemapindex_uri, sitemap_uri, sitemap, sitemapindex_is_file):
        """Read a component sitemap of a Resource List with index

        Each component must be a sitemap with the 
        """
        if (sitemapindex_is_file):
            if (not self.is_file_uri(sitemap_uri)):
                # Attempt to map URI to local file
                remote_uri = sitemap_uri
                sitemap_uri = self.mapper.src_to_dst(remote_uri)
                self.logger.info("Mapped %s to local file %s" % (remote_uri, sitemap_uri))
            else:
                # The individual sitemaps should be at a URL (scheme/server/path)
                # that the sitemapindex URL can speak authoritatively about
                if (self.check_url_authority and
                    not UrlAuthority(sitemapindex_uri).has_authority_over(sitemap_uri)):
                    raise ListBaseIndexError("The sitemapindex (%s) refers to sitemap at a location it does not have authority over (%s)" % (sitemapindex_uri,sitemap_uri))
        try:
            fh = URLopener().open(sitemap_uri)
            self.num_files += 1
        except IOError as e:
            raise ListBaseIndexError("Failed to load sitemap from %s listed in sitemap index %s (%s)" % (sitemap_uri,sitemapindex_uri,str(e)))
        # Get the Content-Length if we can (works fine for local files)
        try:
            self.content_length = int(fh.info()['Content-Length'])
            self.bytes_read += self.content_length
        except KeyError:
            # If we don't get a length then c'est la vie
            pass
        self.logger.info( "Reading sitemap from %s (%d bytes)" % (sitemap_uri,self.content_length) )
        component = sitemap.parse_xml( fh=fh, sitemapindex=False )
        # Copy resources into self, check any metadata
        for r in component:
            self.resources.add(r)
        # FIXME - if rel="up" check it goes to correct place
        # FIXME - check capability

    ##### OUTPUT #####

    def as_xml(self):
        """Return XML serialization of this list

        A single XML serailization does not make sense in the case that the list
        resources is more than is allowed in a single sitemap so will raise an
        exception if that is the case. Otherwise passes to superclass method.
        """
        if (self.max_sitemap_entries is not None):
            if (len(self)>self.max_sitemap_entries):
                raise ListBaseIndexError("Attempt to write single XLM string for list with %d entries when max_sitemap_entries is set to %d" % (len(self),self.max_sitemap_entries))
        return super(ListBaseWithIndex, self).as_xml()

    def write(self, basename='/tmp/sitemap.xml'):
        """Write one or a set of sitemap files to disk

        resources is a ResourceContainer that may be an ResourceList or
        a ChangeList. This may be a generator so data is read as needed
        and length is determined at the end.

        basename is used as the name of the single sitemap file or the 
        sitemapindex for a set of sitemap files.

        Uses self.max_sitemap_entries to determine whether the resource_list can 
        be written as one sitemap. If there are more entries and 
        self.allow_multifile is set true then a set of sitemap files, 
        with an sitemapindex, will be written.
        """
        # Access resources through iterator only
        resources_iter = iter(self.resources)
        ( chunk, next ) = self.get_resources_chunk(resources_iter)
        s = self.new_sitemap()
        if (next is not None):
            # Have more than self.max_sitemap_entries => sitemapindex
            if (not self.allow_multifile):
                raise ListBaseIndexError("Too many entries for a single sitemap but multifile disabled")
            # Work out how to name the sitemaps, attempt to add %05d before ".xml$", else append
            sitemap_prefix = basename
            sitemap_suffix = '.xml'
            if (basename[-4:] == '.xml'):
                sitemap_prefix = basename[:-4]
            # Work out URI of sitemapindex so that we can link up to
            # it from the individual sitemap files
            try:
                index_uri = self.mapper.dst_to_src(basename)
            except MapperError as e:
                raise ListBaseIndexError("Cannot map sitemapindex filename to URI (%s)" % str(e))
            # Use iterator over all resources and count off sets of
            # max_sitemap_entries to go into each sitemap, store the
            # names of the sitemaps as we go
            index=ListBase()
            index.capability_name = self.capability_name
            index.capability_md = self.capability_md
            index.default_capability_and_modified()
            while (len(chunk)>0):
                file = sitemap_prefix + ( "%05d" % (len(index)) ) + sitemap_suffix
                # Check that we can map the filename of this sitemap into
                # URI space for the sitemapindex
                try:
                    uri = self.mapper.dst_to_src(file)
                except MapperError as e:
                    raise ListBaseIndexError("Cannot map sitemap filename to URI (%s)" % str(e))
                self.logger.info("Writing sitemap %s..." % (file))
                f = open(file, 'w')
                chunk.ln.append({'rel': 'up', 'href': index_uri})
                s.resources_as_xml(chunk, fh=f)
                f.close()
                # Record information about this sitemap for index
                r = Resource( uri = uri, path = file,
                              timestamp = os.stat(file).st_mtime,
                              md5 = compute_md5_for_file(file) )
                index.add(r)
                # Get next chunk
                ( chunk, next ) = self.get_resources_chunk(resources_iter,next)
            self.logger.info("Wrote %d sitemaps" % (len(index)))
            f = open(basename, 'w')
            self.logger.info("Writing sitemapindex %s..." % (basename))
            s.resources_as_xml(index,sitemapindex=True,fh=f)
            f.close()
            self.logger.info("Wrote sitemapindex %s" % (basename))
        else:
            f = open(basename, 'w')
            self.logger.info("Writing sitemap %s..." % (basename))
            s.resources_as_xml(chunk, fh=f)
            f.close()
            self.logger.info("Wrote sitemap %s" % (basename))

    def index_as_xml(self):
        """Return XML serialization of this list taken to be sitemapindex entries

        """
        self.default_capability_and_modified()
        s = self.new_sitemap()
        return s.resources_as_xml(self,sitemapindex=True)

    ##### Utility #####

    def get_resources_chunk(self, resource_iter, first=None):
        """Return next chunk of resources from resource_iter, and next item
        
        If first parameter is specified then this will be prepended to
        the list.

        The chunk will contain self.max_sitemap_entries if the iterator 
        returns that many. next will have the value of the next value from
        the iterator, providing indication of whether more is available. 
        Use this as first when asking for the following chunk.
        """
        chunk = ListBase()
        chunk.capability_name = self.capability_name
        chunk.capability_md = self.capability_md
        chunk.default_capability_and_modified()
        if (first is not None):
            chunk.add(first)
        for r in resource_iter:
            chunk.add(r)
            if (len(chunk)>=self.max_sitemap_entries):
                break
        # Get next to see whether there are more resources
        try:
            next = resource_iter.next()
        except StopIteration:
            next = None
        return(chunk,next)
 
    def is_file_uri(self, uri):
        """Return true if uri looks like a local file URI, false otherwise
        
        Test is to see whether have either an explicit file: URI or whether
        there is no scheme name.
        """
        return(re.match('file:',uri) or not re.match('\w{3,4}:',uri))
