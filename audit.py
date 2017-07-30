from collections import defaultdict
import numpy
import pprint
import re
import xml.etree.cElementTree as ET

PATH = "../../_data"
FILE = "bcn.min.osm"
ATTR_INT = ['id', 'uid', 'version', 'changeset']

# RegEx
timestamp1 = re.compile(r'[0-9]{4}[-][0-9]{2}[-][0-9]{2}[T]')
timestamp2 = re.compile(r'[0-9]{2}[:][0-9]{2}[:][0-9]{2}[Z]')
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

# Used by load_nodes_data() and load_tag_map() for manual testing and
# correction purposes
ID = set()
UID = set()
CHANGESET = set()
VERSION = set()
LAT = set()
LON = set()
TIMESTAMP = set()
KS = dict()
VS = dict()


def audit_nodes(f):

    n_id = set()
    n_street_types = defaultdict(int)
    n_key_types = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}

    # Used at the end of audit_nodes() to evaluate if the arrtib if is unique
    total_nodes = 0

    # load_nodes_data() collects each attribute from both nodes and tags into
    # sets. It is only intended for manual testing with the numpy library.
    # load_nodes_data(f)

    for _, element in ET.iterparse(f):

        if element.tag == "node":
            total_nodes += 1
            # Store node_id for further reference in Error messages
            node_id = element.attrib["id"]
            n_id.add(node_id)

            # Loop through the fields expected to be int within a certain
            # range (id, uid, version, changeset) to detect possible problems
            for att in ATTR_INT:
                v = element.attrib[att]

                # isInt() checks if a number can be casted to integer
                if not isInt(v):
                    raise ValueError("Invalid attrib.{} in node {}".format(att, node_id))

                # inRange() checks if a number sits between a predefined range
                if not inRange(v, att):
                    raise ValueError("Detected out of range value for attrib.{} in node {}".format(att, node_id))

            # Latitude and Longitude
            lat = element.attrib["lat"]
            lon = element.attrib["lon"]

            # isFloat() checks if a number can be casted to float
            if not isFloat(lat):
                raise ValueError("Invalid attrib.lat in node {}".format(node_id))
            if not isFloat(lon):
                raise ValueError("Invalid attrib.lon in node {}".format(node_id))

            # inBCN() checks if a pair of coordinates match the city location
            if not inBCN(lat, lon):
                raise ValueError("Invalid set of coordinates in node {}".format(node_id))

            # Timestamp
            tstamp = element.attrib["timestamp"]

            # properDate() checks through a RegEx if a given timestamp follows
            # the correct format
            if not properDate(tstamp):
                raise ValueError("Invalid timestamp format in node {}".format(node_id))

            # For each node, loop through all its tags
            for tag in element.iter("tag"):

                # tag_qc() checks if a tag element has 2 attributes (k, v)
                if not tag_qc(tag):
                    raise ValueError("Tag in node {} had too many attributes".format(node_id))

                # load_tag_map() lists all keys and values found in tags. It is
                # only intended for manual testing and correction purposes;
                # Its output is printed at the end of audit_nodes()
                # all_keys, all_values = load_tag_map(tag, KS, VS)

                # is_street_name() checks if the attribute k == addr:street
                if is_street_name(tag):
                    street_name = tag.attrib["v"]
                    audit_street_type(n_street_types, street_name)

                # audit_key_type() looks for format problems in the keys
                audit_key_type(tag, n_key_types)

    if not len(n_id) == total_nodes:
        raise ValueError("Found attribte id not unique")

    # Prints a list of all the keys found in tags
    # print "\nALL KEYS", "\n", "="*8
    # pprint.pprint(all_keys)
    # Prints a list of all the values found in tags
    # print "\nALL VALUES", "\n", "="*10
    # pprint.pprint(all_values)

    # Prints a list of all the street types found in the data set
    print "\nNODES: STREET TYPES", "\n", "="*19
    print_sorted_dict(n_street_types)
    # Prints a list of the key types based on audit_key_type()
    print "\nNODES: KEY TYPES", "\n", "="*16
    print_sorted_dict(n_key_types)
    return


def audit_ways(f):

    w_id = set()
    w_street_types = defaultdict(int)
    w_key_types = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}

    total_ways = 0

    for _, element in ET.iterparse(f):

        if element.tag == "way":
            total_ways += 1
            # Store way_id for further reference in Error messages
            way_id = element.attrib["id"]
            w_id.add(way_id)

            # Loop through the fields expected to be int within a certain
            # range (id, uid, version, changeset) to detect possible problems
            for att in ATTR_INT:
                v = element.attrib[att]

                # isInt() checks if a number can be casted to integer
                if not isInt(v):
                    raise ValueError("Invalid attrib.{} in way {}".format(att, way_id))

                # inRange() checks if a number sits between a predefined range
                if not inRange(v, att):
                    raise ValueError("Detected out of range value for attrib.{} in way {}".format(att, way_id))

            # Timestamp
            tstamp = element.attrib["timestamp"]

            # properDate() checks through a RegEx if a given timestamp follows
            # the correct format
            if not properDate(tstamp):
                raise ValueError("Invalid timestamp format in way {}".format(way_id))

            # For each way, loop through all its tags
            for tag in element.iter("tag"):

                # tag_qc() checks if a tag element has 2 attributes (k, v)
                if not tag_qc(tag):
                    raise ValueError("Tag in way {} had too many attributes".format(way_id))

                # is_street_name() checks if the attribute k="addr:street"
                if is_street_name(tag):
                    street_name = tag.attrib["v"]
                    audit_street_type(w_street_types, street_name)

                # audit_key_type() looks for format problems in the keys
                audit_key_type(tag, w_key_types)

    if not len(w_id) == total_ways:
        raise ValueError("Found attribte id not unique")

    # Prints a list of all the street types found in the data set
    print "\nWAYS: STREET TYPES", "\n", "="*18
    print_sorted_dict(w_street_types)
    # Prints a list of the key types based on audit_key_type()
    print "\nWAYS: KEY TYPES", "\n", "="*15
    print_sorted_dict(w_key_types)
    return


def isInt(x):
    try:
        if type(int(x)) == int:
            return True
    except ValueError:
        return False


def inRange(v, att):
    length_ref = {'id': 9,
                  'uid': 5,
                  'version': 2,
                  'changeset': 7
                  }
    minlen = length_ref[att] - 3
    maxlen = length_ref[att] + 3
    return minlen <= len(v) <= maxlen


def isFloat(x):
    try:
        if type(float(x)) == float:
            return True
    except ValueError:
        return False


def inBCN(lat, lon):
    lat_check = (41.0 <= float(lat) <= 41.8)
    lon_check = (1.6 <= float(lon) <= 2.5)
    return lat_check and lon_check


def properDate(v):
    break_point = v.find("T")
    v1 = v[:break_point + 1]
    v2 = v[break_point:]
    return timestamp1.search(v1) and timestamp2.search(v2)


def tag_qc(t):
    EXPECTED_ATTR = ["k", "v"]
    UNEXPECTED_ATTR = []
    for key in t.keys():
        if key not in EXPECTED_ATTR:
            UNEXPECTED_ATTR.append(key)
    return len(UNEXPECTED_ATTR) == 0


def is_street_name(t):
    return t.attrib["k"] == "addr:street"


def audit_street_type(street_types, street_name):
    st = street_name.split(' ', 1)[0]
    if st:
        street_types[st] += 1


def audit_key_type(element, keys):
    if lower.search(element.attrib["k"]):
        keys["lower"] += 1
    elif lower_colon.search(element.attrib["k"]):
        keys["lower_colon"] += 1
    elif problemchars.search(element.attrib["k"]):
        keys["problemchars"] += 1
    else:
        keys["other"] += 1
    return keys


def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v)


def load_tag_map(t, ks, vs):

    k = t.attrib["k"]
    v = t.attrib["v"]

    if k in ks:
        ks[k] += 1
    else:
        ks[k] = 1

    if v in vs:
        vs[v] += 1
    else:
        vs[v] = 1

    return ks, vs


def load_nodes_data(f):
    for _, element in ET.iterparse(f):
        if element.tag == "node":
            ID.add(element.attrib["id"])
            UID.add(element.attrib["uid"])
            CHANGESET.add(element.attrib["changeset"])
            VERSION.add(element.attrib["version"])
            LAT.add(element.attrib["lat"])
            LON.add(element.attrib["lon"])
            TIMESTAMP.add(element.attrib["timestamp"])
    print_stats()
    return


if __name__ == "__main__":
    with open("{}/{}".format(PATH, FILE), "r") as f:
        audit_nodes(f)
        audit_ways(f)
