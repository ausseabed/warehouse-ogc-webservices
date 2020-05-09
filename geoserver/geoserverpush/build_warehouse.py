#!/usr/bin/python3
"""
This script is used to register GeoTiffs into a geoserver instance
Requires environmental variables GEOSERVER_URL, GEOSERVER_ADMIN_PASSWORD and LIST_PATH

Example:
export GEOSERVER_URL="http://localhost:8080/geoserver"
export GEOSERVER_ADMIN_PASSWORD="###"
export LIST_PATH="https://bathymetry-survey-288871573946.s3-ap-southeast-2.amazonaws.com/registered_files.json"
"""

from __future__ import print_function

import os
import sys

from connection_parameters import ConnectionParameters
from product_database import ProductDatabase
from product_record import ProductRecord
import time
from workspace_add_task import WorkspaceAddTask
from style_add_task import StyleAddTask
from coverage_add_task import CoverageAddTask
from raster_add_task import RasterAddTask
import logging

logging.basicConfig(level=logging.INFO)


class BuildWarehouse():

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

        product_database = ProductDatabase()
        product_database.load_from_commandline()
        product_records = product_database.get_records()

        WorkspaceAddTask(configuration, self.workspace_name).run()
        StyleAddTask(configuration, self.workspace_name).run()
        CoverageAddTask(configuration, self.workspace_name,
                        product_records).run()

        RasterAddTask(configuration, self.workspace_name,
                      product_records).run()

        # RasterAddTask()
        # StyleAddTask()
        # GroupLayerAddTask()

        # Import rasters into geoserver for each entry in database
        # for source_tif_entry in product_records:
        #     geoserver_bath_raster = source_tif_entry.get_bathymetric_raster()
        #     geoserver_bath_raster_ref = geoserver_catalog_services.add_raster(
        #         geoserver_bath_raster)
        #     geoserver_catalog_services.add_style_to_raster(geoserver_bath_raster_ref["name"],
        #                                                    geoserver_catalog_services.BATH_STYLE_NAME)

        #     geoserver_hs_raster = source_tif_entry.get_hillshade_raster()
        #     if geoserver_hs_raster.source_tif != "":
        #         geoserver_hs_raster_ref = geoserver_catalog_services.add_raster(
        #             geoserver_hs_raster)
        #         geoserver_catalog_services.add_style_to_raster(geoserver_hs_raster_ref["name"],
        #                                                        geoserver_catalog_services.BATH_HILLSHADE_STYLE_NAME)
        #         geoserver_catalog_services.group_layers(
        #             [geoserver_hs_raster, geoserver_bath_raster],
        #             [geoserver_catalog_services.BATH_HILLSHADE_STYLE_NAME,
        #                 geoserver_catalog_services.BATH_STYLE_NAME],
        #             geoserver_hs_raster_ref["bbox"]
        #         )


if __name__ == '__main__':
    warehouse = BuildWarehouse("ausseabedDebugB")
    # warehouse = BuildWarehouse("ausseabed")
    warehouse.register_data_with_geoserver()
    # populate_geoserver()
