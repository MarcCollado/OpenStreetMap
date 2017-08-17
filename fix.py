# -*- coding: utf-8 -*-
import re

import audit

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

EXPECTED = ["avinguda", "carrer", "camí", "carretera", "gran",
            "parc", "passatge", "passeig",
            "plaça".decode('utf-8'), "rambla",
            "ronda", "travessera", "via"]

LANG_MAPPING = {"acceso": "Accés",
                "avenida": "Avinguda",
                "calle": "Carrer",
                "camino": "Camí",
                "paseo": "Passeig",
                "plaza": "Plaça".decode('utf-8'),
                "vía": "Via"
                }

MAPPING = {"av": "Avinguda",
           "av.": "Avinguda",
           "c": "Carrer",
           "c.": "Carrer",
           "carrar": "Carrer",
           "carrerde": "Carrer",
           "carrerl": "Carrer",
           "cl": "Carrer",
           "cr": "Carrer",
           "ctra": "Carretera",
           "ctra.": "Carretera",
           "pg.": "Passeig",
           "pg": "Passeig",
           "pas": "Passeig",
           "pl.": "Plaça".decode('utf-8'),
           "pl": "Plaça".decode('utf-8'),
           "pla": "Plaça".decode('utf-8'),
           "rembla": "Rambla"
           }

NON_CASE = ["de", "del", "la", "el", "i"]

# n_xxx keep track of the number of fixes applied to the data set
n_fix_lang = 0


def map_node(element, node_attr_fields):
    node_attribs = {}
    for attr in element.attrib:
        if attr in node_attr_fields:
            node_attribs[attr] = element.attrib[attr]
    return node_attribs


def map_way(element, way_attr_fields):
    way_attribs = {}
    for attr in element.attrib:
        if attr in way_attr_fields:
            way_attribs[attr] = element.attrib[attr]
    return way_attribs


def get_tags(element, unique_id,
             problem_chars,
             default_tag_type):

    tags = []
    # NODE/WAY_TAGS_FIELDS
    for tag in element.iter("tag"):
        t = {}
        # NODE/WAY_TAGS_FIELDS[0]:id
        # id maps to the top level node/way id attribute value
        t["id"] = unique_id

        # NODE/WAY_TAGS_FIELDS[1]:key
        # if there's no ":" key maps to the full "k" attribute
        # if there's ":" key only maps to the characters after the colon
        # NODE/WAY_TAGS_FIELDS[3]:type
        # type maps to the characters before the colon in the tag
        # type equals "regular" if there's no ":"
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
        v = tag.attrib["v"]

        if audit.is_postcode(tag):
            if len(int(v)) != 5:
                v = None

        if audit.is_street_name(tag):
            st_type = get_street_type(v)
            st_name = v[len(st_type) + 1:]

            if st_type.lower() in LANG_MAPPING:
                v = fix_lang(st_type, st_name)

            elif st_type.lower() in EXPECTED:
                st_type = fix_case(st_type)
                st_name = fix_case(st_name)
                v = st_type + " " + st_name

            elif st_type.lower() in MAPPING:
                st_type = MAPPING[st_type.lower()]
                st_name = fix_case(st_name)
                v = st_type + " " + st_name

            else:
                print "\nUNCAUGHT STREET TYPES", "\n", "="*21
                print st_type  # + " " + st_name

        # value maps to the full "v" attribute
        t["value"] = v
        tags.append(t)
    return tags


def get_street_type(v):
    street_type = v.split(' ', 1)[0]
    return street_type


def fix_case(s):
    d = []
    s_array = s.split()
    for e in s_array:
        if e in NON_CASE:
            d.append(e)
            continue

        if "\'" in e and len(e) > 3:
            p = e.find("\'")
            temp = e[p-1].lower() + e[p] + e[p+1].upper() + e[p+2:].lower()
            d.append(temp)
            continue
        else:
            temp = e[0].upper() + e[1:].lower()
            d.append(temp)
    s_fix_case = " ".join(d)
    return s_fix_case


def fix_lang(st_type, st_name):
    st_type_fix_lang = LANG_MAPPING[st_type.lower()]
    street_fix_lang = st_type_fix_lang + ' ' + st_name
    return street_fix_lang
