# -*- coding: utf-8 -*-
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus

import fix
import schema

NODES_PATH = "data/node.csv"
NODE_TAGS_PATH = "data/node_tags.csv"
WAYS_PATH = "data/way.csv"
WAY_NODES_PATH = "data/way_nodes.csv"
WAY_TAGS_PATH = "data/way_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset',
               'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def process_map(file_in, validate):
    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


def shape_element(element,
                  node_attr_fields=NODE_FIELDS,
                  way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):

    nodes = {}
    ways = {}
    way_nodes = []
    tags = []

    if element.tag == "node":
        # Map node attributes according to schema
        nodes = fix.map_node(element, node_attr_fields)
        # Map node tags according to schema
        tags = fix.get_tags(element, nodes["id"], PROBLEMCHARS, 'regular')

    if element.tag == "way":
        # Map way attributes according to schema
        ways = fix.map_way(element, way_attr_fields)
        # Map way tags according to schema
        tags = fix.get_tags(element, ways["id"], PROBLEMCHARS, 'regular')

        # WAY_NODES_FIELDS
        i = 0
        for nd in element.iter("nd"):
            w = {}

            # WAY_NODES_FIELDS[0]:id
            # id maps to the top level way id attribute value
            w["id"] = ways["id"]

            # WAY_NODES_FIELDS[1]:node_id
            # node_id maps to the ref attribute value of the nd tag
            w["node_id"] = nd.attrib["ref"]

            # WAY_NODES_FIELDS[2]:position
            # position maps to the index starting at 0 of the nd tag
            w["position"] = i
            i += 1
            way_nodes.append(w)

    if element.tag == 'node':
        return {'node': nodes, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': ways, 'way_nodes': way_nodes, 'way_tags': tags}


# Helper Functions provided by Udacity
def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
