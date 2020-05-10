import sys
import os
import requests
from product_record import ProductRecord
import logging


class ProductDatabase():
    """ 
    Product Database data structure (at the moment a json formatted file that has the form:
 [
  {"l3ProductTifLocation": "s3://bucket-name/name-of-file.tif",
  "hillshadeLocation": "s3://bucket-name/name-of-file.tif",
  "l0CoverageLocation": "s3://bucket-name/name-of-file.shp"
  "gazeteerName":"e.g. Beagle Commonwealth Marine Reserve",
  "year":2018,
  "resolution":"1m",
  "UUID":"68f44afd-78d0-412f-bf9c-9c9fdbe43968"}, "metadataPersistentId":"",...
    """

    def load_from_commandline(self):
        try:
            self.source_tif_path = os.environ['LIST_PATH']
        except KeyError:
            logging.exception("Please set the environment variable LIST_PATH")
            sys.exit(1)

        logging.info("Path to file that specifies what to load (LIST_PATH) = " +
                     self.source_tif_path)

    def get_records(self):
        # Step 1 - read in a list of source tifs
        response = requests.get(self.source_tif_path)
        if not response.ok:
            logging.error("Error trying to get LIST_PATH")

        self.source_tifs = response.json()

        logging.info("Number of source_tifs: " + str(len(self.source_tifs)))

        results = [ProductRecord(x) for x in self.source_tifs]

        return results
