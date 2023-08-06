from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from transmogrify.pathsorter.treeserializer import TreeSerializer
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer

import logging
import urllib
import urlparse
from lxml import etree

class OsmSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = TreeSerializer(transmogrifier, name, options, previous)
        self.context = transmogrifier.context
        self.normalizer = queryUtility(IIDNormalizer)

        self.type = 'wasgehtengine.Venue'
        self.logger = logging.getLogger(name)
        self.basepath = 'venues/'
        
    def process_tags(self, item, elem):
        for tag in elem.xpath('tag'):
            
            # If node has a name, use it for path instead of ID
            if tag.get('k') == 'name':
                item['_path'] = self.basepath + self.normalizer.normalize(tag.get('v'))
                item['title'] = tag.get('v')
                
            elif tag.get('k') == 'contact:website' or tag.get('k') == 'website':
                # need to convert internationalized domain names to pure ascii hostnames
                website = tag.get('v').encode('idna')
                
                url = urlparse.urlparse(website)
                        
                if not url.scheme:
                    url = urlparse.urlparse('http://' + website)
                            
                item['website'] = url.geturl()
            elif tag.get('k').startswith('addr:'):
                item['postal_address'][tag.get('k')[5:]] = tag.get('v')
            elif tag.get('k') == 'contact:phone':
                item['phone_number'] = tag.get('v')             
            else:
                item['osm_element_tags'][tag.get('k')] = tag.get('v')
                
    def calculate_area_centroid(self, item, tree, elem):
        
        way_id = elem.get('id')
        nodes = tree.xpath("/osm/node[@id = /osm/way[@id = '" + way_id + "']/nd/@ref]")

        lat = sum([float(node.xpath('@lat')[0]) for node in nodes]) / len(nodes) 
        lon = sum([float(node.xpath('@lon')[0]) for node in nodes]) / len(nodes)
        
        return lat, lon
        

    def __iter__(self):
        for item in self.previous:
            
            if 'ignore' in item and item['ignore'] == True:
                yield item
                continue
            
            query_params = item['query_params']

            f = urllib.urlopen('http://www.overpass-api.de/api/xapi?' + query_params)
            
            tree = etree.parse(f)
            
            for elem in tree.xpath("/osm/*[tag/@k = 'name']"):
                item = { 'query_params' : query_params }
                item['_type'] = self.type
                item['creators'] = ['osm-venue-importer']
                item['osm_element_id'] = elem.get('id')
                item['transitions'] = ["publish"]
                item['postal_address'] = {}
                
                item['osm_element_type'] = 'Node' if elem.tag == 'node' else 'Way'
                item['osm_element_tags'] = {}
                
                if elem.get('lat'):
                    item['latitude'] = elem.get('lat')
                    item['longitude'] = elem.get('lon')
                else:
                    centroid = self.calculate_area_centroid(item, tree, elem)
                    item['latitude'] = centroid[0]
                    item['longitude'] = centroid[1]
                
                self.process_tags(item, elem)
                self.logger.info('Importing venue "'+ item['title'] + '"')
                
                yield item
                item = None