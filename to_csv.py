import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema

PATH = "../../_data"
FILE = "bcn.min.osm"

NODES_PATH = "output/node.csv"
NODE_TAGS_PATH = "output/node_tags.csv"
WAYS_PATH = "output/way.csv"
WAY_NODES_PATH = "output/way_nodes.csv"
WAY_TAGS_PATH = "output/way_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset',
               'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS,
                  way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == "node":

        # NODE_FIELDS
        for attr in element.attrib:
            if attr in node_attr_fields:
                node_attribs[attr] = element.attrib[attr]

        # NODE_TAGS_FIELDS
        tags = get_tags(element, node_attribs["id"])

    if element.tag == "way":

        # WAY_FIELDS
        for attr in element.attrib:
            if attr in way_attr_fields:
                way_attribs[attr] = element.attrib[attr]

        # WAY_TAGS_FIELDS
        tags = get_tags(element, way_attribs["id"])

        # WAY_NODES_FIELDS
        i = 0
        for nd in element.iter("nd"):
            w = {}

            # WAY_NODES_FIELDS[0]:id
            w["id"] = way_attribs["id"]

            # WAY_NODES_FIELDS[1]:node_id
            w["node_id"] = nd.attrib["ref"]

            # WAY_NODES_FIELDS[2]:position
            w["position"] = i
            i += 1

            way_nodes.append(w)

    if element.tag == 'node':
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def get_tags(element, uid,
             problem_chars=PROBLEMCHARS,
             default_tag_type='regular'):

    tags = []
    # NODE/WAY_TAGS_FIELDS
    for tag in element.iter("tag"):
        t = {}
        # NODE/WAY_TAGS_FIELDS[0]:id
        t["id"] = uid
        # NODE/WAY_TAGS_FIELDS[1]:key
        # NODE/WAY_TAGS_FIELDS[3]:type
        k = tag.attrib["k"]
        m = problem_chars.search(k)
        if not m:
            if ":" not in k:
                t["key"] = k
                t["type"] = default_tag_type
            else:
                cut = k.find(":") + 1
                t["key"] = k[cut:]
                t["type"] = k[:cut - 1]
        else:
            t["type"] = default_tag_type
        # NODE/WAY_TAGS_FIELDS[2]:value
        t["value"] = tag.attrib["v"]
        tags.append(t)
    return tags


#               Main Function                        #
# ================================================== #
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


if __name__ == '__main__':
    OSM_PATH = "{}/{}".format(PATH, FILE)
    process_map(OSM_PATH, validate=False)
