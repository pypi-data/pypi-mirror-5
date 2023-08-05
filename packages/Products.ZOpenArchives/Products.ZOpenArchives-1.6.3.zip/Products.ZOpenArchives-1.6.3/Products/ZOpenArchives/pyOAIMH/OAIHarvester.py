# -*- coding: iso-8859-15 -*-

#################################################################################
#                                       #
# Copyright (C) 2000-2003 Steve Giraud, Eric Brun, Benoit Charles,      #
# Alexandre Desoubeaux, Igor Barma, David McCuskey, Jean-Michel Cez         #
# Christian Martel                              #
#                                       #
# This program is free software; you can redistribute it and/or         #
# modify it under the terms of the GNU General Public License           #
# as published by the Free Software Foundation; either version 2        #
# of the License, or (at your option) any later version.            #
# This program is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                 #
# GNU General Public License for more details.                                  #
#                                                                               #
# You should have received a copy of the GNU General Public License             #
# along with this program; if not, write to the Free Software           #
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.   #
#                                       #
#################################################################################

__doc__ = """ Class which implements the OAI harvester protocol """

import transaction

import httplib
import StringIO
from xml.sax import make_parser, saxutils
from xml.sax.handler import ContentHandler 
import xml.dom.minidom

from CreateURL import CreateURL

from MyXMLLib import MyXMLLib
import DateTime, sys
# import timeoutsocket
# from socket import error

class HTTPLibError(Exception): pass

class ServerError(Exception): pass


class OAIHarvester(MyXMLLib):

    default_encoding = 'UTF-8'

    # gives tag path within XML structure to
    #   use to retrieve information. differences between
    #   OAI protocol versions
    #
    dompaths = {
        '1.1': {
          'protocolVersion':['Identify','protocolVersion'],
          'repositoryName':['Identify','repositoryName'],
          'baseURL':['Identify','baseURL'],
          'adminEmail':['Identify','adminEmail'],
          'description':['Identify','description'],
          
          'metadataFormat':['ListMetadataFormats','metadataFormat']
        },
        
        '2.0':{
          'protocolVersion':['OAI-PMH','Identify','protocolVersion'],
          'repositoryName':['OAI-PMH','Identify','repositoryName'],
          'baseURL':['OAI-PMH','Identify','baseURL'],
          'adminEmail':['OAI-PMH','Identify','adminEmail'],
          'description':['OAI-PMH','Identify','description'],
          'earliestDatestamp':['OAI-PMH','Identify','earliestDatestamp'],
          'deletedRecord':['OAI-PMH','Identify','deletedRecord'],
          'compression':['OAI-PMH','Identify','compression'],
          'granularity':['OAI-PMH','Identify','granularity'],
          
          'metadataFormat':['OAI-PMH','ListMetadataFormats','metadataFormat']
        }
        }

    
    def __init__(self, site_host, site_url, oai_set=''):
        """ """

        # host and url for OAI server
        #
        self.site_host = site_host
        self.site_url = site_url
        if oai_set == "":
            oai_set = None
        self.oai_set = oai_set
        self.site_status = { 'lastUpdate':None,
                             'status': 'unknown',
                             'lastRequest':None
                             }
        
        # site_identify
        #   first group is must includes
        #   second is may include multiples
        self.site_identify = { 'repositoryName':'',
                               'baseURL':'',
                               'protocolVersion':'1.1',
                               'earliestDatestamp':'',
                               'deletedRecord':'',
                               'granularity':'',
                               'adminEmail':[],
                               
                               'compression':None,
                               'description':[]
                               }
        
        # list of site's available metadata
        #
        self.site_metadata = { 'oai_dc':
                               {'schema':'',
                                'metadataNamespace':'',
                                'metadataPrefix':'oai_dc'}
                               }
        
        # list of available set
        self.site_sets = {}


    def initialize(self):
        """
        issue_Identify - get OAI site information from URL
        """
        self.issue_Identify()
        self.issue_ListMetadataFormats()
        self.issue_ListSets()


    def updateObject(self):
        """
        updates older objects
        """
        self.site_status={'lastUpdate':'',
                          'status': '',
                          'lastRequest':''}

    def handle_Error(self, errors):
        """
        put error in site
        returns 0 on OK,
        other for error codes
        """
        if len(errors) > 0:
            the_error = errors[0]
            #print "!! GOT ERROR !! ", the_error.attributes['code']
            #print self.getDOMElementText(the_error)
            return 1
        else:
            # print " no errors "
            return 0

   
    def get_dompath(self, name, version=None):
        """
        give back the datapath list given
        name and version
        """
        if version==None:
            version = self.get_protocolVersion().strip()
        if not self.dompaths.has_key(version):
            #print "version '%s' not found " % (version)
            return None
        
        paths = self.dompaths[version]
        if not paths.has_key(name):
            #print "name '%s' not found in version '%s'" % (name, version)
            return None
        
        return paths[name]
    


    ###############################
    #### ATTRIBUTE ACCESSOR METHODS


    #### site Host
    
    def get_siteHost(self):
        """ return site status """
        
        return self.site_host

    def set_siteHost(self, site_host):
        """ return site status """
        
        self.site_host=site_host

    #### site URL       

    def get_siteURL(self):
        """ return site status """
        
        return self.site_url

    def set_siteURL(self, site_url):
        """ return site status """
        
        self.site_url=site_url
        
    #### OAI set
    def get_oaiSet(self):
        """return oai set"""
        try:
            return self.oai_set
        except:
            self.set_oaiSet(None)
        return self.oai_set
        
    def set_oaiSet(self, oai_set):
        """set oai set"""
        if oai_set == "":
            oai_set = None
        self.oai_set = oai_set
        

    #### site status
        
    def get_siteStatus(self, section):
        """ return site status """
        if section not in self.site_status.keys():
            raise "incorrect seciton for siteStatus ", section
        
        return self.site_status[section]
     
    def set_siteStatus(self, section, value):
        """ """
        if section not in self.site_status.keys():
            raise "incorrect seciton for siteStatus ", section

        self.site_status[section] = value

    
    #### protocolVersion
    
    def set_protocolVersion(self, version=''):
        """ """
        self.site_identify['protocolVersion'] = version


    def get_protocolVersion(self):
        """ """
        if self.site_identify.has_key('protocolVersion'):
            return self.site_identify['protocolVersion']
        else:
            return None

    #### repositoryName
        
    def set_repositoryName(self, name=''):
        """ """
        self.site_identify['repositoryName'] = name

    def get_repositoryName(self):
        """ """
        if self.site_identify.has_key('repositoryName'):
            return self.site_identify['repositoryName']
        else:
            return None
        
    #### baseURL
        
    def set_baseURL(self, url=''):
        """ """
        self.site_identify['baseURL'] = url

    def get_baseURL(self):
        """ """
        if self.site_identify.has_key('baseURL'):
            return self.site_identify['baseURL']
        else:
            return None
        
    #### earlistDatestamp
        
    def set_earliestDatestamp(self, datestamp=''):
        """ """
        self.site_identify['earliestDatestamp'] = datestamp

    def get_earliestDatestamp(self):
        """ """
        if self.site_identify.has_key('earliestDatestamp'):
            return self.site_identify['earliestDatestamp']
        else:
            return None
        
    #### deletedRecord
        
    def set_deletedRecord(self, record=''):
        """ """
        self.site_identify['deletedRecord'] = record

    def get_deletedRecord(self):
        """ """
        if self.site_identify.has_key('deletedRecord'):
            return self.site_identify['deletedRecord']
        else:
            return None
        
    #### granularity
        
    def set_granularity(self, granularity=''):
        """ """
        self.site_identify['granularity'] = granularity

    def get_granularity(self):
        """ """
        if self.site_identify.has_key('granularity'):
            return self.site_identify['granularity']
        else:
            return None
        
    #### description
        
    def set_description(self, description_list=[]):
        """ """
        self.site_identify['description'] = description_list

    def get_description(self):
        """ """
        if self.site_identify.has_key('description'):
            return self.site_identify['description']
        else:
            return None
        
    #### compression
        
    def set_compression(self, compression=''):
        """ """
        self.site_identify['compression'] = compression

    def get_compression(self):
        """ """
        if self.site_identify.has_key('compression'):
            return self.site_identify['compression']
        else:
            return None
                
    #### adminEmail    

    def set_adminEmail(self, admin_list=[]):
        """ """
        self.site_identify['adminEmail']=admin_list
    
    def get_adminEmail(self):
        """ returns a list of email addresses """
        if self.site_identify.has_key('adminEmail'):
            return self.site_identify['adminEmail']
        else:
            return []

    #### site host
        
    def get_siteHost(self):
        """ """
        return self.site_host
        
    def get_site_sets(self):
        """
        """
        if not hasattr(self, 'site_sets'):
            self.site_sets = {}
        return self.site_sets


    ###########################
    ###### principal methods

    def do_updateSite(self):
        """
        get updates from site - Identify, ListMetadataFormats, ListRecords
        """

        # TODO: update will also need to check
        #   existing records for deletions on server, etc

        self.set_siteStatus('lastRequest', DateTime.DateTime().aCommon())
    
        self.issue_Identify()
        self.issue_ListMetadataFormats()
        self.issue_ListSets()
        #### add by jecez for manage oai_dc prefix in portal #################
        namespaces = getattr(self.aq_parent,'Namespaces')
        lNameSpaceMetaDataPrefix = []
        for nm in namespaces.objectValues():
            lNameSpaceMetaDataPrefix.append(nm.get_nsPrefix())
            
        #for metadata_prefix in self.site_metadata.keys():
        for metadata_prefix in  self.site_metadata.keys():
            #print "metadataPrefix", metadata_prefix
            if metadata_prefix in lNameSpaceMetaDataPrefix:
        ########## end ########################################################
                self.issue_ListRecords( oai_metadataPrefix = metadata_prefix, oai_set = self.oai_set )
            
        self.set_siteStatus('lastUpdate', DateTime.DateTime().aCommon())


        
    def issue_Identify(self):
        """
        method to issue the 'oai/?verb=Identify' request
        """
        # print "in issue_Identify"
        
        self.current_request = { 'verb':'Identify' }
        url_obj = CreateURL(self.current_request )
        url = url_obj.getURL()
        
        try:
            returncode, returnmsg, headers, data = self.http_connect('?' + url)
            if returncode == 200:
                self.set_siteStatus('status', 'Available')
                
                dom = xml.dom.minidom.parseString(data)

                #if self.handle_Error(dom.getElementsByTagName("error")) != 0:
                    #print "ERROR !! ", data

                self.handle_Identify(dom=dom)
                
        except:
            import traceback
            traceback.print_exc()
            #print "error Identify"
            self.set_siteStatus('status', 'Unavailable')
            raise HTTPLibError

        self.current_request = None
        
        if returncode != 200:
            self.set_siteStatus('status', "%s (%s)" % (returnmsg,returncode) )
            raise ServerError


    def handle_Identify(self, dom=None):
        """
        we need to process the DOM from issue_Identify
        look for tags and put info in object attribs
        """
        # print "#### in handle_Identify"
        
        # retrieve protocolVersion - single
        #   is chicken before egg scenario
        #   which type of protocol to use before getting protocol
        #   use getElementsByTagName because it will get everything
        #
        node_list = dom.getElementsByTagName('protocolVersion')
        if len(node_list) != 1: raise "too many protocolVersions"
        for node in node_list:
            self.set_protocolVersion(self.getDOMElementText(node))

        # retrieve repositoryName - single
        #
        path = self.get_dompath('repositoryName')
        node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        if len(node_list) != 1: raise "too many repositoryNames"
        for node in node_list:
            self.set_repositoryName(self.getDOMElementText(node))

        # retrieve baseURL - single
        #
        path = self.get_dompath('baseURL')
        node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        if len(node_list) != 1: raise "too many baseURL"
        for node in node_list:
            self.set_baseURL(self.getDOMElementText(node))

        # retrieve adminEmail - multiple
        #
        path = self.get_dompath('adminEmail')
        node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
        admin_list = []
        for node in node_list:
            admin_list.append(self.getDOMElementText(node))

        self.set_adminEmail(admin_list)


        # description - multiple (optional)
        #
        path = self.get_dompath('description')
        if path == None:
            self.set_description('N/A')
        else:
            desc_list = []
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            for node in node_list:
                desc_list.append(self.getDOMElementText(node))
                
            self.set_description(desc_list)


        ## these are for 2.0
        
        # retrieve earliestDatestamp - single
        #
        path = self.get_dompath('earliestDatestamp')
        if path == None:
            self.set_earliestDatestamp('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            if len(node_list) != 1: raise "too many deletedRecords"
            for node in node_list:
                self.set_earliestDatestamp(self.getDOMElementText(node))

        # retrieve deletedRecord - single
        #
        path = self.get_dompath('deletedRecord')
        if path == None:
            self.set_deletedRecord('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            if len(node_list) != 1: raise "too many deletedRecords"
            for node in node_list:
                self.set_deletedRecord(self.getDOMElementText(node))

        # granularity - single
        #
        path = self.get_dompath('granularity')
        if path == None:
            self.set_granularity('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            if len(node_list) != 1: raise "too many granularity"
            for node in node_list:
                self.set_granularity(self.getDOMElementText(node))

        # compression - single (optional)
        #
        path = self.get_dompath('compression')
        if path == None:
            self.set_compression('N/A')
        else:
            node_list = self.findDOMElements(dom_list=[dom], tag_path=path)
            for node in node_list:
                self.set_compression(self.getDOMElementText(node))



    def handle_Resume(self, resumeToken ):
        """
        look for resumeToken field
        """
        # print "### in handle Resume"

        if len(resumeToken.childNodes) > 0:
            return self.getDOMElementText(resumeToken)
        return None


    def issue_ListSets(self):
        """
        method to issue the 'oai/?verb=ListSets'

        req args : none

        get list from site
          parse xml
          store results

        """       
        self.current_request = { 'verb':'ListSets'}
        url_obj = CreateURL( self.current_request )
        url = url_obj.getURL()

        #try:
        if 1:
            returncode, returnmsg, headers, data = self.http_connect('?'+url)
            if returncode == 200:
                self.set_siteStatus('status', 'Available')
                dom = xml.dom.minidom.parseString(data)
                metadom_list = dom.getElementsByTagName("set")
                self.handle_ListSets(dom_list=metadom_list)
                
        #except:
        #    self.set_siteStatus('status', 'Unavailable')
        #    raise HTTPLibError

        self.current_request = None
        
        
        if returncode != 200:
            self.site_sets = {}
            # We do nothing due the fact the repository doesn't maybe don't handle ListSets verb...
            #self.set_siteStatus('status', "%s (%s)" % (returnmsg,returncode) )
            #raise ServerError
        

    def handle_ListSets(self, dom_list=[]):
        """
        process set DOM elements given from
          issue_ListSets()
          
        get each DOM
           save tag info in dict
           
        """
        self.site_sets = {}
        for set in dom_list:
            dict = {}
            for element in set.childNodes:
                if hasattr(element, 'tagName'):
                    tag_name= element.tagName
                    tag_info = self.getDOMElementText(element, self.default_encoding)
                    if tag_name == 'setDescription':
                        tag_info = element.toxml(self.default_encoding)
                    dict[tag_name] = tag_info
            
            self.site_sets[dict['setName']]=dict
            
    def issue_ListMetadataFormats(self, oai_identifier=None):
        """
        method to issue the 'oai/?verb=ListMetadataFormats'

        req args : none
        opt args : ID of record

        get list from site
          parse xml
          store results

        """
        # print "### in issue_ListMetadataFormats"
        
        self.current_request = { 'verb':'ListMetadataFormats',
                                 'identifier':oai_identifier
                                 }
        url_obj = CreateURL( self.current_request )
        url = url_obj.getURL()

        try:
            returncode, returnmsg, headers, data = self.http_connect('?'+url)

            if returncode == 200:
                self.set_siteStatus('status', 'Available')
                dom = xml.dom.minidom.parseString(data)
                #if self.handle_Error(dom.getElementsByTagName("error")) != 0:
                #    print "ERROR !! ", data
            

                # find <records> in DOM
                #
                path = self.get_dompath('metadataFormat') 
                metadom_list = self.findDOMElements(dom_list=[dom], tag_path=path)

                # print "metadom ", metadom_list
                self.handle_ListMetadataFormats(dom_list=metadom_list)
                
        except:
            #print "error List metaformats "
            self.set_siteStatus('status', 'Unavailable')
            raise HTTPLibError


        ###
        #
        self.current_request = None
        
        if returncode != 200:
            self.set_siteStatus('status', "%s (%s)" % (returnmsg,returncode) )
            raise ServerError
        

    def handle_ListMetadataFormats(self, dom_list=[]):
        """
        process metadata format DOM elements given from
          issue_ListMetadataFormats()
          
        get each DOM
           save tag info in dict
           
        """
        # print "#### in handle_ListMetadataformats"
        # reinitialize site_metadata before update
        self.site_metadata = {}
        for format in dom_list:
            dict = {}
            for element in format.childNodes:
                if hasattr(element, 'tagName'):
                    tag_name= element.tagName
                    tag_info = self.getDOMElementText(element, self.default_encoding)

                    dict[tag_name] = tag_info
                    
            # TODO: check for existance of at least 'oai_dc'
            #  it's a minimum requirement in OAI spec
            self.site_metadata[dict['metadataPrefix']]=dict
            
        
    def issue_ListRecords(self, oai_metadataPrefix, oai_from=None,
                          oai_until=None, oai_set=None):
        """
        method to issue the 'oai/?verb=ListRecords&metadataPrefix=oai_dc'

        req args = metadataPrefix
        opt args = from, until, set (setSpec)
        exc args = resumptionToken
        
        get records from site
          create objects if necessary
          update ones which exist
          get next batch if more
        """
        # print "### in issue_ListRecords "

        
        # save this info until the end, so we can now
        #   a little about the request (metadataPrefix)
        #
        count = 0        
        self.current_request =  { 'verb':'ListRecords',
                                  'metadataPrefix':oai_metadataPrefix,
                                  'from':oai_from,
                                  'until':oai_until,
                                  'set':oai_set,
                                  }
        url_obj = CreateURL( self.current_request )
        while 1:
            url = url_obj.getURL()
            try:
                returncode, returnmsg, headers, data = self.http_connect('?'+url)                                
                if returncode != 200:
                    print "erreur sur la connection"
                    break
                else:
                    self.set_siteStatus('status', 'Available')
                    try:
                        data = data.decode('utf-8')
                    except:
                        try:
                            data = data.decode('iso-8859-1')
                        except:
                            try:
                                data = data.decode('ascci')  
                            except:
                                pass
                    data = data.encode('utf-8')         
                    dom = xml.dom.minidom.parseString(data)
                                      
                    if self.handle_Error(dom.getElementsByTagName("error")) != 0:
                        break
                    
                    count = self.handle_ListRecords(dom.getElementsByTagName("ListRecords"), count)
                                        
                    resume_node = dom.getElementsByTagName("resumptionToken")
                    if resume_node == None or len(resume_node) == 0:
                        break

                    resumeToken_value = self.handle_Resume(resume_node[0])
                    if resumeToken_value == None:
                        break
                    url_obj.addProperty( { 'resumptionToken':resumeToken_value } )
                    url_obj.delProperty( ['metadataPrefix','from','until','set','setSpec'] )
                    print "resumptionToken"
                    print resumeToken_value
                    print "**------------------------**"
                    
            except:
                import traceback
                traceback.print_exc()
                #print "error List Records "
                #import sys
                #print sys.exc_type; sys.exc_value
            
                self.set_siteStatus('status', 'Unavailable')
                raise HTTPLibError

        # outside of the WHILE
        #
        self.current_request = None
              
        if returncode != 200:
            self.set_siteStatus('status', "%s (%s)" % (returnmsg,returncode) )
            #print "error List Records "
            #import traceback;
            #traceback.print_exc();
            raise ServerError    
        

    def handle_ListRecords(self, ListRecords, count):
        """
        calls handle_addOAIRecord on all records found:
          this is a hook for a subclass to implement
        """
        # print "### in handle_ListRecords "
        if len(ListRecords) > 0:
            i = 0
            the_ListRecord = ListRecords[0]
            for record in the_ListRecord.getElementsByTagName("record"):
                i = i+1
                count += 1
                self.handle_addOAIRecord( dom=record )
                print count
                if i%10:
                    transaction.savepoint()
        return count

    def handle_addOAIRecord(self, record):
        """
        override this method
        get <record> DOM node
        depends on the database you have
        """
        #print "override OAIHarvester.handle_addOAIRecord"
        #print record.toxml('UTF-8')
        

    def http_connect(self, get_url):
        """
        connect to site given GET url
        return connection results
        """
        h = httplib.HTTPConnection(self.site_host)      
        h.connect()
        if sys.version_info[0] >= 2 and sys.version_info[1] >= 3:
            h.sock.settimeout(120.0)
        else:
            h.sock.set_timeout(120)

        h.request('GET', self.site_url + get_url)
        r1 = h.getresponse()
        returncode = r1.status
        returnmsg = r1.reason
        headers = r1.msg
        data = None
        if returncode == 200:  # OK
            data = r1.read()
        h.close()
        return ( returncode, returnmsg, headers, data )
    
