# OpenStreetMap
Data Wrangling Project — Udacity Data Analyst Nanodegree

IMPORTANT: The whole project is documented and explained in the OpenStreetMap.md file.


## Main Scripts

* `app.py`: calls the rest of the functions and executes the program. By commenting some of the lines, some functionalities can be turned on/off.

* `audit.py`: this is the first look at the data. It programmatically checks for data validity, accuracy and other measures and prints its results in the terminal. It does not modify the data itself, only reports the issues it encounters.

The script consists of two similar modules:

  * audit_nodes(): checks for `node` elements.
  * audit_ways(): checks for `way` elements.

Running both at the same time could lead to parsing errors, therefore it is recommended to leave one of them commented in the `app.py` script and run the other separately after the first has finished.

* `to_csv.py`: reads in the data from the `.osm` file and exports all the data to `.csv` files. During the process, it ensures the export is compliant with the structure dictated by `schema.py`.

For data validity it focuses more on semantics rather than format, but unlike `audit.py`, `to_csv.py` treats and modifies (through `fix.py`) any data related problems described in the **Part II** of the `OpenStreetMap.md` document.

* `to_sql.py`: after the data has been stored in `.csv` files, `to_sql.py` creates a database `osm.db` and the necessary tables matching the structure described in `schema.py`.


## Support Features

* `fix.py`: contains all the data wrangling functions used by `to_csv.py`.

* `compress.py`: takes an `.osm` file as an input and outputs a k-reduced version of it. k is a parameter that can be changed in the code.

* `schema.py`: schema of how the data will be exported from the `.osm` file to the database.
