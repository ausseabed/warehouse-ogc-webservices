import gs_rest_api_coveragestores
from gs_rest_api_coveragestores.rest import ApiException
from gs_rest_api_coveragestores.model.coverage_store_info import CoverageStoreInfo
from gs_rest_api_coveragestores.model.coverage_store_info_wrapper import CoverageStoreInfoWrapper
import gs_rest_api_coverages
from gs_rest_api_coverages.rest import ApiException
from gs_rest_api_coverages.model.coverage_info import CoverageInfo
from gs_rest_api_coverages.model.coverage_info_wrapper import CoverageInfoWrapper
from gs_rest_api_coverages import MetadataEntry

import os
import sys
import logging
from product_record import ProductRecord
from typing import List
from product_database import ProductDatabase

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, SurveyL3Relation, Survey
import re


class RasterAddTask(object):

    def __init__(self, configuration, workspace_name, product_database: ProductDatabase):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_database = product_database

    def create_raster(self, display_name, display_description, url_location, srs, metadata):

        native_layer_name = re.sub(
            ".tif", "", re.sub(".*/", "", url_location))
        logging.info(
            "Creating coveragestore for raster {}".format(display_name))

        logging.info("Metadata link: {}".format(metadata))
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_client = gs_rest_api_coveragestores.ApiClient(
            self.configuration, header_name='Authorization', header_value=authtoken)

        # NOTE for non-public services, we will have some work to do here
        url = url_location + \
            "?useAnon=true&awsRegion=AP_SOUTHEAST_2"  # ap-southeast-2

        coverage_store_info = gs_rest_api_coveragestores.CoverageStoreInfo(
            name=display_name, description=display_description,
            type="S3GeoTiff", workspace=self.workspace_name, enabled=True,
            url=url)

        coverage_store_info_wrapper = gs_rest_api_coveragestores.CoverageStoreInfoWrapper(
            coverage_store=coverage_store_info)

        # create an instance of the API class
        cs_api_instance = gs_rest_api_coveragestores.DefaultApi(api_client)

        try:
            cs_api_instance.post_coverage_stores(
                coverage_store_info_wrapper, self.workspace_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->post_coverage_store_upload: %s\n" % e)
            return

        if (metadata == ""):
            metadata_link_entry = None
        else:
            metadata_link_entry = {'metadataLink': [
                {'type': 'text/html', 'metadataType': 'ISO19115:2003', 'content': metadata}]}
        # create an instance of the API class
        api_instance = gs_rest_api_coverages.DefaultApi(
            gs_rest_api_coverages.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))
        # CoverageInfo | The body of the coverage to POST
        coverage_info = gs_rest_api_coverages.CoverageInfo(
            name=display_name, native_name=native_layer_name, title=display_name, srs=srs, metadata_links=metadata_link_entry)
        # data = "<coverage><name>{}</name><title>{}</title><nativeName>{}</nativeName><srs>{}</srs></coverage>".format(
        #    display_name, display_name, native_layer_name, srs)
        workspace = self.workspace_name  # str | The name of the workspace
        store = display_name  # str | The name of the coverage data store

        body = gs_rest_api_coverages.CoverageInfoWrapper(coverage_info)
        try:
            api_instance.post_workspace_coverage_store(body, workspace, store)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->post_workspace_coverage_store: %s\n" % e)
            logging.error(
                "Please manually remove coverage store {} before next attempt to submit".format(display_name))
            logging.error(
                "The input params were native_layer_name: {} display_name: {} display_description: {} url_location: {} srs: {} metadata: {}".format(
                    native_layer_name, display_name, display_description, url_location, srs, metadata))

    def get_coverages(self):
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_coveragestores.DefaultApi(
            gs_rest_api_coveragestores.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        workspace = self.workspace_name

        try:
            # Get a list of all coverage stores in {workspace}
            api_response = api_instance.get_coverage_stores(workspace)
            logging.info(api_response)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_coverage_stores: %s\n" % e)

        if api_response['coverageStores'] == '':
            raster_names = []
        else:
            raster_names = [raster_record['name']
                            for raster_record in api_response['coverageStores']['coverageStore']]
        return raster_names

    raster_presentation_string = "{0} OV"
    hillshade_presentation_string = "{0} HS"

    def get_coverage_name(self, product_l3_dist: ProductL3Dist):
        # match on prod_id
        self.product_database.get_name_for_product(
            product_l3_dist, self.raster_presentation_string)
        self.product_database.get_name_for_product(
            product_l3_dist, self.hillshade_presentation_string)

    def run(self):

        existing_rasters = self.get_coverages()
        logging.info("Found existing rasters {}".format(existing_rasters))

        # First worry about bathymetry, then hillshade
        product_record: ProductL3Dist
        for product_record in self.product_database.l3_products:
            bath_display_name = self.product_database.get_name_for_product(
                product_record, self.raster_presentation_string)

            # Add bathymetry Raster
            if bath_display_name in existing_rasters:
                logging.info("Already have raster coveragestore: {}".format(
                    bath_display_name))
            else:
                self.create_raster(
                    bath_display_name, bath_display_name,
                    product_record.bathymetry_location, product_record.source_product.srs,
                    product_record.source_product.metadata_persistent_id)

            hs_display_name = self.product_database.get_name_for_product(
                product_record, self.hillshade_presentation_string)

            if product_record.hillshade_location == "":
                logging.info("No hillshade raster defined for: {}".format(
                    hs_display_name))
            elif hs_display_name in existing_rasters:
                logging.info("Already have raster coveragestore: {}".format(
                    hs_display_name))
            else:
                self.create_raster(
                    hs_display_name, hs_display_name,
                    product_record.hillshade_location, product_record.source_product.srs,
                    product_record.source_product.metadata_persistent_id)
