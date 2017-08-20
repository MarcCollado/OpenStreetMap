# OpenStreetMap Data Project


### Map Area

Barcelona, Barcelona, Spain

According to Wikipedia, [Barcelona](https://en.wikipedia.org/wiki/Barcelona) is *"the capital city of the autonomous community of Catalonia in the Kingdom of Spain, as well as the country's second most populous municipality, with a population of 1.6 million within city limits".*

Nonetheless, its urban area extends beyond the administrative city limits with a population of around 4.7 million people, being the largest metropolis on the Mediterranean Sea — which curiously enough, I wasn't aware of.

* [openstreetmap.org](https://www.openstreetmap.org/relation/347950)
* [mapzen.com](https://mapzen.com/data/metro-extracts/metro/barcelona_spain/)

Barcelona is my hometown and that's the ultimate reason I chose this map for the project. Beyond this fact I'm interested in working with this data to further explore street naming and formatting differences, compared to the United States data, which has been the main focus until now. But also to understand the data's linguistic impact having two languages coexisting at the same time, since both Catalan and Spanish are official languages in the city.

The downloaded data was provided directly by Mapzen, since the area I intended to download from OpenStreetMap was too large. Above I provided both links in case you wanted to run the code with the original dataset.


## Project Outline

The project consists of three distinct parts:

* **Visualize and audit:** carried out by the `audit.py`, this section is intended to make sense of the data as a whole and assess its quality. This routine will programmatically check for data validity, accuracy and other measures seen throughout the course materials.
* **Export and fix:** `audit.py` will reveal problems with the map data and provide the necessary information to create a data cleaning plan to execute on. Bear in mind that `audit.py` won't perform any modification on the data itself, but rather print on the terminal the problems that it has encountered. After this first audition, and unlike `audit.py`, it'll be `to_csv.py` job to export the data according to a predetermined schema, but also programmatically fix the semantic mistakes it finds along the way.
* **Visualizing the data:** once audited and fixed, this last section will consist on revealing the most interesting insights of the data.


## Part I: Visualize and Audit

In this part the data will be mapped out and visualized, programmatically checking for possible quality flaws. At the end of the day the data should be ready to fit a structure that will look like the schema found at `schema.py`.

The audit process will be mainly concerned by two data points: nodes and ways. Each element also contains relevant information within, that will be kept and translated to aforementioned data structure.

Regardless the sample file reveals most fields are self descriptive, they will be further analyzed one by one to understand the data behind them and watch out for quality issues.


### Auditing nodes

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

This function iterates through the XML looking for tags named `nodes` and then performs a series of actions in order to reveal potentially problematic data.

Here's the summary of the actions `audit_nodes()` will carry out:

* `changeset, id, uid, version`: despite there is not much information about what these numbers actually mean or represent, a quick look at the raw data reveals they are integers within a certain range. `audit_nodes()` will loop through each of them ensuring they can be casted as integers and watching out for outliers outside a reasonable range. On top of that, `audit_nodes()` will also assume that `id` must be unique.
* `lat, lon`: latitude and longitude coordinates are easier to audit, since they are expected to map something inside the area delimited by the city. Therefore, according to Google Maps, its range should be approximately enclosed within the latitude [41.0 - 41.8] and longitude [1.6 to 2.5] and can be casted as float.
* `timestamp`: the built-in function checks through a RegEx if the values for timestamp match a given pattern `2017-07-26T11:17:26Z`.

Next up are tags within each node. A quick glimpse at the data reveals that each tag contains two attributes (k, v). The attribute `k` holds information about the specific location, therefore, the ones with the value `addr:street` will contain street data.

`audit_nodes()` will create an ordered list with all the possible street values and also look for the nature of each key: lowercase, colons, but also problematic characters.


### Auditing ways

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

The routine will be looking for `postcode` of 5 digits, starting with `08` (which belong to the Barcelona metro area), `city` names properly capitalized and belonging to the metro area, `housenumber` matching integers and so forth.


## Part II: Export and fix

After the programatic check performed by `audit.py` in the Barcelona area map, five types of problems have shown up:

* Language inconsistency for street types under the second level tag `addr:street` (*Avinguda* vs. *Avenida*)
* Format disparity, case inconsistency, grammar mistakes and over­abbreviation for street types on second level tags `addr:street` (for the correct form *Carrer* there is: *C, CALLE, Calle, Carrar, Carrer, carrer, CR*)
* Street type omission on second level tags `addr:street`, where the street name is displayed directly.
* Cities `addr:city` out of range of the Barcelona metropolitan area.
* Incorrect postal code: Barcelona area postal codes begin with 08XXX, but found some outside this range.


### Language inconsistency

Because Barcelona has two official languages coexisting at the same time, is it possible to find some street prefixes still written in Spanish. Regardless the actual name remains the same, the city council enforces all the street prefixes to be written in Catalan, and that's exactly what `fix_lang()` does.

```
def fix_lang(st_type, st_name):
    st_type_fix_lang = LANG_MAPPING[st_type.lower()]
    street_fix_lang = st_type_fix_lang + ' ' + st_name
    return street_fix_lang
```

It takes in the street name and street type, and then references LANG_MAPPING, a dictionary that contains all the possibles Spanish references to street types. Finally, it returns the correct name in Catalan.

For example, the entries such *"Avenida Diagonal"* become *"Avinguda Diagonal".*


### Street types: format problems

The data contained several format problems, like over­abbreviation, typos and incorrect naming.

First the data was screened with regular expressions and data type validation through `audit.py`. Once there was a clear view of the problems the data presented, they got fixed through `fix.py` functions, called via the `shape_element()` function found in `to_csv.py`.

Finally, `fix.py` also implements some "hard-coded" data, such as `EXPECTED` or `MAPPING` to manually fix the errors not caught by the programatic functions. This sets are being updated in real time as more rare cases appear.


### Incorrect postal codes

The data also included some cities and postal codes outside the Barcelona area. All the postal codes from Barcelona have 5 digits and start with "08". During the data prep before exporting to the csv files, the data is programmatically checked and flagged as `None` in case a wrong postal code is found.

```
if audit.is_postcode(tag):
        if len(v) != 5:
            v = None
        elif v[:2] != "08":
            v = None
```

But not just Barcelona...

A simple query listing all the cities under the tag key "city" quickly revealed the data was not only from Barcelona, but the whole metropolitan area, which coincidentally, still retains the two digit "08" start position for the postal codes.

Here's the list of the top 10 cities with more entries:

```
sqlite>
SELECT tags.value, COUNT(tags.value) as count
FROM (SELECT * FROM node_tags UNION ALL
      SELECT * FROM way_tags) as tags
WHERE tags.key = 'city'
GROUP BY tags.value
ORDER BY count DESC
LIMIT 10;
```

```
Barcelona                   9111
Santa Coloma de Cervelló    2967
Badalona                    545
Cornellà de Llobregat       518
El Prat de Llobregat        243
L'Hospitalet de Llobregat   194
Sant Cugat del Vallès       116
Sant Boi de Llobregat       92
Sant Fost de Campsentelles  60
Ripollet                    58
```


### Street type omission and uncaught errors

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

Most of the scenarios were already discussed in the sections above, but the interesting part here is the `else:` statement[1].

All the situations that were not properly filtered are set apart and printed in the terminal to examine what could exactly happen there in order to manually deal with them.


## Part III: Visualizing the Data

This section contains basic statistics and insights of the dataset, the queries used to gather them, and some additional ideas.


### File sizes

```
bcn.osm ........... 255.1 MB
bcn.db ............ 141.9 MB
node.csv ..........  93.6 MB
node_tags.csv .....   8.4 MB
way.csv ...........   8.8 MB
way_tags.csv ......  13.9 MB
way_nodes.cv ......  35.1 MB  
```


### Number of nodes

`sqlite> SELECT COUNT(*) FROM node;`

1130797


### Number of ways

`sqlite> SELECT COUNT(*) FROM way;`

143652


### Cities in the metro area

```
sqlite>
SELECT COUNT(*)
FROM (SELECT tags.value, COUNT(tags.value) as dp
      FROM (SELECT * FROM node_tags UNION ALL
            SELECT * FROM way_tags) as tags
      WHERE tags.key = 'city'
      GROUP BY tags.value
      HAVING dp > 5
      ORDER BY dp DESC) as cities;
```

The query above revealed that there are 32 cities in the metro area with more than 5 entries in the dataset.


### Number of unique users

```
sqlite>
SELECT COUNT(DISTINCT(u.uid))
FROM (SELECT uid FROM node UNION ALL
SELECT uid FROM way) as u;
```

2753


### Top contributors

```
sqlite>
SELECT u.user, COUNT(*) as count
FROM (SELECT user FROM node UNION ALL SELECT user FROM way) as u
GROUP BY u.user
ORDER BY count DESC
LIMIT 10;
```

Top 10 contributors of the dataset:

```
josepmunoz              89400
DanielBautista          80496
EliziR                  72357
Jose Antonio Fontaneda  53221
Raulvior                44499
davidbascones           38455
pitort                  32240
yopaseopor              32012
moogido                 29943
Carlos_Sánchez          26348
```

The results from the top contributors have even more depth than one might think at a first glance.

* The total entries of the dataset, accounting for nodes and ways, adds up to 1274449.
* Up to 498971 entries, almost 40% of the grand total, was reported by the top 10 contributors.
* Yet more stunning, up to 1118092 entries, almost 90% of the grand total, was reported by the top 100 contributors.
* On the other side of the spectrum, more than 55% the users have contributed only 5 entries or less, see the query below.

```
sqlite>
SELECT COUNT(*)
FROM (SELECT u.user, COUNT(*) as count
      FROM (SELECT user FROM node UNION ALL
            SELECT user FROM way) as u
      GROUP BY u.user
      HAVING count < 6);
```

## In-depth Analysis

### Max. Speed

A few years ago all the streets in Barcelona were limited to 50km/h. But a recent effort from the city council to reduce the number of cars populating the streets of the city, there's been a big campaign to reduce the maximum speed from 50 down to 30 km/h.

```
sqlite>
SELECT tags.value, COUNT(*) as count
FROM (SELECT * FROM node_tags UNION ALL
      SELECT * FROM way_tags) as tags
GROUP BY tags.value
HAVING tags.key = 'maxspeed'
ORDER BY count DESC;
```

The query above maps the current speed limits in the city. It clearly shows the city council effort to lower city's speed limit with almost 20% of the metropolitan road already on the newer limit, when a few years ago it was literally zero.

```
50,     3552
30,     1545
80,     908
20,     634
100,    502
60,     430
120,    352
70,     93
310,    47
sign,   3
var,    1
```

Curiously the data also showed some validity error, particularly the `310` being out of range. The data possibly refers to `30`, but it is definitely something that could be avoided with the same process used in `audit_nodes()` for `lat & lon`, since we already know in advance the range [30 - 120] of possible values.

```
def inBCN(lat, lon):
    lat_check = (41.0 <= float(lat) <= 41.8)
    lon_check = (1.6 <= float(lon) <= 2.5)
    return lat_check and lon_check
```

It also revealed another validity error in the case of `sign`, that could be avoided in `audit_nodes()` as well, filtering by data type `int`.


### And finally, tourism

Yet another controversial issue in Barcelona these recent years has been undoubtedly tourism. In just a few years the city has been transformed from a local town to an European capital, hosting millions of tourists per year.

For this reason this last query breaks down the twenty most common type of shops per category:

```
supermarket     673
bakery          352
clothes         234
convenience     220
hairdresser     210
greengrocer     134
kiosk           130
car_repair      107
books           85
car             82
butcher         76
shoes           60
mobile_phone    53
gift            50
florist         49
jewelry         49
bicycle         47
beauty          43
hardware        42
furniture       41
```

Unfortunately the data does not reveal any telling insight about the explosion of a particular category related to tourism. It follows an absolutely logic and expected trend, where the most common type of shops are regular goods such as food, clothes.

Further development could compare how different categories change depending on the neighborhoods: from the ones where locals live and the most touristic spots, but that's definitely beyond the scope of this project :)


## Additional Improvements

By far the most challenging — and also annoying, problem I have encountered wrangling the data has been the validity and consistency of each data point.

The fact users are contributing each piece of data, makes it virtually impossible to ensure data quality. For example, this is a chunk of a query displaying cities in the metro area:

```
St. Feliu
Sant feliu de Ll.
Sant Feliu de Llobregat
sant Feliu de Llobregat
sant Feliu de llob.
sant feliu de llobregat
```

Note that the name we are looking for is "Sant Feliu de Llobregat", but carelessness when it comes to report the data is consistently messing up with the results.

I could address some of the problems in `audit.py` and `to_csv.py`, but the deepness of the data makes it really difficult to programmatically track down each input.

My suggestion would definitely come in the form of pre-validation for data entries. I don't think that would fix 100% of the problems, but at least these simple measures would account for a much cleaner dataset:

* Data type: if a value has to be an integer, ban the possibility of reporting a string. See for example the case with latitude or max_speed.
* Range: if it is known that a value has to be within a predetermined range, flag the ones outside.
* Autocompletion or "did you mean...": if there are 3.000 entries under the key "Barcelona", once a "b" is typed, show a dropdown with the most possible outcomes.

The data was properly cleaned for the exercise purposes, but it the whole set was incomplete and messier than I thought when I started. The most I tinkered with it, the most I discovered flaws and data problems that couldn't be fixed programatically. This is the ultimate reason why I think this improvement would make a lot of difference.

---
[1] In the final version of the code, the uncaught errors handling process has been updated to save all the misfits in a set() rather than printing each result one by one.
