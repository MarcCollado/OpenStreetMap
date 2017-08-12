# OpenStreetMap Data Project


### Map Area

Barcelona, Barcelona, Spain

According to Wikipedia, [Barcelona](https://en.wikipedia.org/wiki/Barcelona) is the capital city of the autonomous community of Catalonia in the Kingdom of Spain, as well as the country's second most populous municipality, with a population of 1.6 million within city limits.

Nonetheless, its urban area extends beyond the administrative city limits with a population of around 4.7 million people, being the largest metropolis on the Mediterranean Sea — which curiously enough, I wasn't aware of.

* [openstreetmap.org](https://www.openstreetmap.org/relation/347950)
* [mapzen.com](https://mapzen.com/data/metro-extracts/metro/barcelona_spain/)

Barcelona is my hometown and that's the ultimate reason I chose this map for the project. Beyond this fact, I'm interested in working with this data to further explore street naming and formatting differences, compared to the United States. But also to understand the linguistic impact on the data of having two languages coexisting at the same time, since both Catalan and Spanish are official languages in the city.

The downloaded data was provided directly by Mapzen, since the area I intended to download from OpenStreetMap was too large. Above I provided both links in case you wanted to run the code with the original data set.


## Project Outline

The project consists of three distinct parts:

* Visualize and audit: carried out by the `audit.py` file, this section is intended to make sense of the data as a whole and assess its quality. This routine will programmatically check for data validity, accuracy and other measures seen throughout the course materials.
* Spot and fix: `audit.py` will ultimately reveal problems with the map and provide the necessary information to create a data cleaning plan to execute on. This section will detail the problems encountered and the `fix.py` file will address them.
* Visualizing the data: once audited and fixed, this last section consists on revealing the most interesting insights of the data.


## Part I: Visualize and Audit

In this part the data will be mapped out and visualized, programmatically checking for possible quality flaws. At the end of the day the data should be ready to fit a structure that will look like the schema found at `schema.py`.

The audit process will be mainly concerned by two data points: nodes and ways. Each element also contains relevant information within, that will be kept and translated to aforementioned data structure.

Regardless the sample file reveals most fields are self descriptive, they will be further analyzed one by one to understand the data behind them and watch out for quality issues.


### Auditing Nodes

The node element can be found across the data file under the `<node></node>` tag, here's a sample:

```
<node changeset="43251231" id="269379908" lat="41.3911687" lon="2.1394864" timestamp="2016-10-28T17:46:08Z" uid="500572" user="yopaseopor" version="8">
  <tag k="bicycle" v="use_sidepath" />
  <tag k="highway" v="traffic_signals" />
  <tag k="addr:street" v="Avinguda Diagonal" />
</node>
```

According to the `schema.py`, nodes will be mapped to the following schema:

**Node Element Structure**

* node: dictionary
  * id
  * user
  * uid
  * version
  * lat
  * lon
  * timestamp
  * changeset
  * node_tags: list of dictionaries
    * id
    * key
    * value
    * type

The auditing will be performed in the `audit.py` file, in the case of nodes, particularly through the `audit_nodes()` function.

This function iterates through the XML looking for tags named *nodes* and then performs a series of actions in order to reveal potentially problematic data.

Here's the summary of the actions `audit_nodes()` will carry out:

* `changeset, id, uid, version`: despite there is not much information about what these numbers actually mean or represent, a quick look at the raw data reveals they are integers within a certain range. `audit_nodes()` will loop through each of them ensuring they can be casted as integers and watching out for outliers outside a reasonable range. On top of that, `audit_nodes()` will also assume that `id` must be unique.
* `lat, lon`: latitude and longitude coordinates are easier to audit, since they are expected to map something inside the area delimited by the city. Therefore, according to Google Maps, its range should be approximately enclosed within the latitude [41.0 - 41.8] and longitude [1.6 to 2.5] and can be casted as float.
* `timestamp`: the built-in function checks through a RegEx if the values for timestamp match a given pattern `2017-07-26T11:17:26Z`.

Next up are tags within each node. A quick glimpse at the data reveals that each tag contains two attributes (k, v). The attribute *k* holds information about the specific location, therefore, the ones with the value `addr:street` will contain street data.

`audit_nodes()` will create an ordered list with all the possible street values and also look for the nature of each key: lowercase, colons, but also problematic characters.


### Auditing Ways

After the audit of the nodes, checking for ways is rather easy since both data structures share most of the elements and schema.

Regardless, the function `audit_ways()`, which is a carbon copy of its brother `audit_nodes()` and rely on the same helper functions, goes through the same process seen in Auditing Nodes.

The way element can be found across the data file under the `<way></way>` tag and its structure differs a little bit from the node, here’s a sample:

```
<way changeset="24261522" id="48043182" timestamp="2014-07-20T20:08:52Z" uid="37608" user="micha_k" version="3">
  <nd ref="30686299" />
  <nd ref="2972006300" />
  <nd ref="30686300" />
  <tag k="name" v="Carrer de Santa Eulàlia" />
  <tag k="layer" v="-1" />
  <tag k="tunnel" v="yes" />
  <tag k="highway" v="tertiary" />
</way>
```

According to the `schema.py`, ways will be mapped to the following schema:

    **Way Element Structure**

    * way: dictionary
      * id
      * user
      * uid
      * version
      * timestamp
      * changeset
      * way_nodes: list of dictionaries
        * id
        * node_id
        * position
      * way_tags: list of dictionaries
        * id
        * key
        * value
        * type


### Other checks

Finally, using a combination of the lighter `quick_print()` and `load_nodes_data()` functions, the data coming from all the tags containing the value "addr" will be evaluated for consistency.

The routine will be looking for `postcode` of 5 digits, starting with 0, `city` names properly capitalized, `housenumber` matching integers and so forth.


## Part II: Spot and Fix

After the programatic check performed by `audit.py` in the Barcelona area map, five types of problems have shown up:

* Language inconsistency for street types under the second level tag `addr:street` (*Avinguda* vs. *Avenida*)
* Format disparity, case inconsistency, grammar mistakes and over­abbreviation for street types on second level tags `addr:street` (for the correct form *Carrer* there is: *C, CALLE, Calle, Carrar, Carrer, carrer, CR*)
* Street type omission on second level tags `addr:street`, where the street name is displayed directly.
* Cities `addr:city` out of range of the Barcelona metropolitan area.
* Incorrect postal code: Barcelona area postal codes begin with 08XXX, but found some outside this range.


### Language Inconsistency

Because Barcelona has two official languages coexisting at the same time, is it possible to find some street prefixes still written in Spanish. Regardless the actual name remains the same, the city council enforces all the street prefixes to be written in Catalan, and that's exactly what `fix_lang()` does.

```
def fix_lang(st_type, st_name):
    st_type_fix_lang = LANG_MAPPING[st_type.lower()]
    street_fix_lang = st_type_fix_lang + ' ' + st_name
    return street_fix_lang
```

It takes in the street name and street type, and then references LANG_MAPPING, a dictionary that contains all the possibles Spanish references to street types. Finally, it returns the correct name in Catalan.

For example, the entries such *"Avenida Diagonal"* become *"Avinguda Diagonal".*


## Street types: Format problems

The data contained several format problems, like over­abbreviation, typos and incorrect naming.

First the data was screened with regular expressions and data type validation through `audit.py`. Once there was a clear view of the problems the data presented, they got fixed through `fix.py` functions, called via the `shape_element()` function found in `to_csv.py`.

Finally, `fix.py` also implements some "hard-coded" data, such as `EXPECTED` or `MAPPING` to manually fix the errors not caught by the programatic functions. This sets are being updated in real time as more rare cases appear.


## Street Type Omission and Uncaught Errors

Once all the data has been filtered and processed, the last step is to find rare gems that were uncaught during the process and then, manually act on those by editing the data or creating an additional feature or function to deal with these edge cases.

The `shape_element()` function is structured as a drip and starts filtering case by case:

```
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
            print "\nUNCAUGHT STREET TYPES", "\n", "="*20
            print st_type + " " + st_name
```

Most of the scenarios were already discussed in the sections above, but the interesting part here is the `else:` statement.

All the situations that were not properly filtered are set apart and printed in the terminal to examine what could exactly happen there in order to manually deal with them.


## Part III: Visualizing the Data
