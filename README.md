# OpenStreetMap
Data Wrangling Project — Udacity Data Analyst Nanodegree

## Scripts
`audit.py`: programmatically checks for data validity, accuracy and other measures and prints its results in the terminal. It consists mainly of two similar modules:

* audit_nodes(): checks for `node` elements.
* audit_ways(): checks for `way` elements.

Running both at the same time could lead to parsing errors, therefore it is recommended to leave one of them commented and run the other separately.

* `compress.py`: takes an `.osm` file as an input and outputs a k-reduced version of it. k is a parameter that can be changed in the code.

* `export_schema.py`: schema of how the data will be exported from the `.osm` file to the database.
