#!/usr/bin/python3
"""
This script is used to register GeoTiffs into a geoserver instance
Requires environmental variables GEOSERVER_URL, GEOSERVER_ADMIN_PASSWORD and LIST_PATH

Example:
export GEOSERVER_URL="http://localhost:8080/geoserver"
export GEOSERVER_ADMIN_PASSWORD="###"
export LIST_PATH="https://bathymetry-survey-288871573946.s3-ap-southeast-2.amazonaws.com/registered_files.json"
"""

from dotenv import load_dotenv
import os
import sys

import logging
from auth_broker import AuthBroker
from product_database import ProductDatabase
from connection_parameters import ConnectionParameters
from update_database_action import UpdateDatabaseAction
from step_function_action import StepFunctionAction

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, SurveyL3Relation, Survey
logging.basicConfig(level=logging.DEBUG)
load_dotenv()


class Overlays():

    """ 
    Class that houses connection parameters and reads from a datasource 
    such as environmental variables
    """

    def __init__(self):
        self.settings = ConnectionParameters()
        self.settings.load_from_commandline()

        auth = AuthBroker(self.settings)
        self.token = auth.get_auth_token()

    def run(self):
        product_database = ProductDatabase(self.token)
        product_database.load_from_commandline()
        product_database.download_from_rest()

        logging.info("Found {} source products".format(len(
            [product.id for product in product_database.l3_src_products])))

        logging.info("Found {} products that have been processed".format(len(
            [product.source_product.id for product in product_database.l3_dist_products])))

        processed_product_ids = [product.source_product.id
                                 for product in product_database.l3_dist_products]

        unprocessed_products = [
            product for product in product_database.l3_src_products if product.id not in processed_product_ids]

        logging.info("Planning on processing {} products".format(
            len(unprocessed_products)))

        for unprocessed_product in [unprocessed_products[0]]:
            logging.info("Processing {}".format(unprocessed_product.name))
            step_function_action = StepFunctionAction(unprocessed_product)
            step_function_action.run_step_function()
            update_database_action = UpdateDatabaseAction(
                unprocessed_product, product_database.database_url, self.token)
            update_database_action.update()


if __name__ == '__main__':
    overlays = Overlays()
    overlays.run()
