#!/usr/bin/python3
"""
This script is used to register GeoTiffs into a geoserver instance
Requires environmental variables GEOSERVER_URL, GEOSERVER_ADMIN_PASSWORD and LIST_PATH

Example:
export GEOSERVER_URL="http://localhost:8080/geoserver"
export GEOSERVER_ADMIN_PASSWORD="###"
export LIST_PATH="https://bathymetry-survey-288871573946.s3-ap-southeast-2.amazonaws.com/registered_files.json"
"""

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, SurveyL3Relation, Survey
from dotenv import load_dotenv
import os
import sys

from connection_parameters import ConnectionParameters
from product_database import ProductDatabase
import time
from workspace_add_task import WorkspaceAddTask
from style_add_task import StyleAddTask
# from test_add_task import TestAddTask
from coverage_add_task import CoverageAddTask
from raster_add_task import RasterAddTask
from raster_style_attach_task import RasterStyleAttachTask
from group_layer_task import GroupLayerTask
from service_description_add_task import ServiceDescriptionAddTask
import logging
from auth_broker import AuthBroker
from pythonjsonlogger import jsonlogger
from metadata_cache import MetaDataCache

handler = logging.StreamHandler()  # Or FileHandler or anything else
# Configure the fields to include in the JSON output. message is the main log string itself
format_str = '%(message)%(levelname)%(name)%(asctime)'
formatter = jsonlogger.JsonFormatter(format_str)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
# Normally we would attach the handler to the root logger, and this would be unnecessary
logger.propagate = False
load_dotenv()


class PushGeoserverSettings():

    def __init__(self, workspace_name='ausseabed'):
        self.workspace_name = workspace_name

    """
    Class that houses connection parameters and reads from a datasource
    such as environmental variables
    """

    def register_data_with_geoserver(self):
        settings = ConnectionParameters()
        settings.load_from_commandline()
        configuration = settings.create_configuration()

        auth = AuthBroker(settings)
        token = auth.get_auth_token()

        product_database = ProductDatabase(token)
        product_database.load_from_commandline()
        product_database.download_from_rest()

        meta_cache = MetaDataCache()

        WorkspaceAddTask(configuration, self.workspace_name).run()
        ServiceDescriptionAddTask(configuration, self.workspace_name).run()
        StyleAddTask(configuration, self.workspace_name).run()
        CoverageAddTask(configuration, self.workspace_name,
                        product_database, meta_cache).run()

        RasterAddTask(configuration, self.workspace_name,
                      product_database, meta_cache).run()

        RasterStyleAttachTask(configuration, self.workspace_name,
                              product_database).run()

        GroupLayerTask(configuration, self.workspace_name,
                       product_database, meta_cache).run()

        # TestAddTask(configuration, self.workspace_name, product_database).run()

        logging.info("Completed")


if __name__ == '__main__':
    warehouse = PushGeoserverSettings("ausseabed")
    warehouse.register_data_with_geoserver()
