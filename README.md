# OpenStreetMap
Data Wrangling Project — Udacity Data Analyst Nanodegree

## Scripts
* `audit.py`: programmatically checks for data validity, accuracy and other measures and prints its results in the terminal. It consists mainly of two similar modules:

  * audit_nodes(): checks for `node` elements.
  * audit_ways(): checks for `way` elements.

Running both at the same time could lead to parsing errors, therefore it is recommended to leave one of them commented and run the other separately.

* `to_csv.py`: reads in the data from the `.osm` file. It treats and fixes any data related problems described in the **Part II** of the `OpenStreetMap.md` document. Finally, as the name indicates, exports all the treated data to `.csv` files.

* `to_sql.py`: after the data has been stored in `.csv` files, `to_sql.py` creates a database `osm.db` and the necessary tables matching the structure described in `schema.py`.

* `compress.py`: takes an `.osm` file as an input and outputs a k-reduced version of it. k is a parameter that can be changed in the code.

* `schema.py`: schema of how the data will be exported from the `.osm` file to the database.
