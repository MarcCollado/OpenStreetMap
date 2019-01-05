# 🗺 OpenStreetMap Data
Data Wrangling Project — Udacity Data Analyst Nanodegree

This project belongs to Udacity's [Data Analyst Nanodegree](https://eu.udacity.com/course/data-analyst-nanodegree--nd002). Below you'll find the rest of the Nanodegree projects and I also wrote a [short post](https://www.collado.io/blog/2018/udacity-dand) in my blog about the course experience.

* [Intro to data analysis](https://github.com/MarcCollado/titanic)
* [Exploratory data analysis](https://github.com/MarcCollado/wine)
* [Data wrangling](https://github.com/MarcCollado/open-street-map)
* [Machine learning](https://github.com/MarcCollado/enron)
* [Data visualization](https://public.tableau.com/profile/marccollado#!/vizhome/TitanicFinal_6/Titanic)

ℹ️ This project was developed in 2017 during the Nanodegree and it is no longer maintained. If you'd like to see what I'm currently working on, please, visit my [now page](https://www.collado.io/now).


## Tech Stack
The project was built with:

* Python 2.7
* [NumPy](http://www.numpy.org/)
* SQL Database


## File Structure
The entire project is documented and explained in the [`OpenStreetMap.md`](https://github.com/MarcCollado/open-street-map/blob/master/OpenStreetMap.md) file, I encourage you to start there.

Here's the file structure:

* `app.py`: calls all the functions and executes the program. To create the .csv files and import the data to the database in the `data` folder, just run `python app.py` and the script will take care of the rest. `app.py` can also run `audit.py` functions, but those are commented by default since they don't cause any modification to the data itself.
* `audit.py`: this is the first look at the data. It programmatically checks for data validity, accuracy and other measures and prints its results in the terminal. It does not modify the data itself, only reports the issues it encounters.

The script consists of two similar modules:

  * audit_nodes(): checks for `node` elements.
  * audit_ways(): checks for `way` elements.

Running both at the same time could lead to parsing errors, therefore it is recommended to leave one of them commented in the `app.py` script and run the other separately after the first has finished.

* `to_csv.py`: reads in the data from the `.osm` file and exports all the data to `.csv` files. During the process, it ensures the export is compliant with the structure dictated by `schema.py`.
For data validity it focuses more on semantics rather than format, but unlike `audit.py`, `to_csv.py` treats and modifies (through `fix.py`) any data related problems described in the **Part II** of the `OpenStreetMap.md` document.
* `to_sql.py`: after the data has been stored in `.csv` files, `to_sql.py` creates a database `osm.db` and the necessary tables matching the structure described in `schema.py`.

### Helpers
* `fix.py`: contains all the data wrangling functions used by `to_csv.py`.
* `compress.py`: takes an `.osm` file as an input and outputs a k-reduced version of it. k is a parameter that can be changed in the code.
* `schema.py`: schema of how the data will be exported from the `.osm` file to the database.
