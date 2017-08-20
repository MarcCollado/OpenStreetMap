# -*- coding: utf-8 -*-
import audit
import to_csv
import to_sql
import time

PATH = "data/"
FILE = "bcn_sample.osm"
OSM_PATH = "{}/{}".format(PATH, FILE)

if __name__ == "__main__":
    with open("{}/{}".format(PATH, FILE), "r") as f:
        # audit.quick_print(f)
        # audit.audit_nodes(f)
        # audit.audit_ways(f)
        pass
    to_csv.process_map(OSM_PATH, validate=False)
    time.sleep(5)
    to_sql.main()
