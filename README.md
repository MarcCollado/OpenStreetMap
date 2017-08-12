# OpenStreetMap
Data Wrangling Project — Udacity Data Analyst Nanodegree


## Main Scripts

* `app.py`: calls the rest of the functions and executes the program. By commenting some of the lines there you can turn on/off some funcionalities.

* `audit.py`: programmatically checks for data validity, accuracy and other measures and prints its results in the terminal. It does not modify data, only reports issues. It mainly consists of two similar modules:

  * audit_nodes(): checks for `node` elements.
  * audit_ways(): checks for `way` elements.

Running both at the same time could lead to parsing errors, therefore it is recommended to leave one of them commented in the `app.py` script and run the other separately.

* `to_csv.py`: reads in the data from the `.osm` file. It treats and fixes (through `fix.py`) any data related problems described in the **Part II** of the `OpenStreetMap.md` document. Finally, as the name indicates, exports all the treated data to `.csv` files.

  * `fix.py`: contains all the data wrangling functions used by `to_csv.py`.

* `to_sql.py`: after the data has been stored in `.csv` files, `to_sql.py` creates a database `osm.db` and the necessary tables matching the structure described in `schema.py`.


## Support Features

* `compress.py`: takes an `.osm` file as an input and outputs a k-reduced version of it. k is a parameter that can be changed in the code.

* `schema.py`: schema of how the data will be exported from the `.osm` file to the database.
