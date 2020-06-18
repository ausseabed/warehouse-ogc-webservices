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

from gis_metadata.iso_metadata_parser import IsoParser

from gis_metadata.metadata_parser import get_metadata_parser
import requests


class RasterAddTask(object):

    def __init__(self, configuration, workspace_name, product_database: ProductDatabase):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_database = product_database

    @staticmethod
    def get_abstract(metadata_url):
        logging.info("Loading metadata: %s\n" % metadata_url)
        if not(metadata_url.startswith("http://pid") or metadata_url.startswith("https://pid")):
            return metadata_url

        try:
            metadata_response = requests.get(
                metadata_url + "?_format=text%2Fxml")
            if (metadata_response.ok):
                iso_from_file = get_metadata_parser(metadata_response.text)
                return iso_from_file.convert_to(dict)['abstract'] + '\n\n' + metadata_url
            else:
                logging.error(
                    "Could not download metadata from: %s\n" % metadata_url)

        except Exception:
            logging.exception(
                "Could not load metadata from: %s\n" % metadata_url)
            return metadata_url

    def create_raster(self, display_name, title, url_location, srs, metadata, dimensions):

        native_layer_name = re.sub(
            ".tiff?$", "", re.sub(".*/", "", url_location))
        logging.info(
            "Creating coveragestore for raster {} = {}".format(display_name, native_layer_name))

        logging.info("Metadata link: {}".format(metadata))
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_client = gs_rest_api_coveragestores.ApiClient(
            self.configuration, header_name='Authorization', header_value=authtoken)

        # NOTE for non-public services, we will have some work to do here
        url = url_location + \
            "?useAnon=true&awsRegion=AP_SOUTHEAST_2"  # ap-southeast-2

        display_description = RasterAddTask.get_abstract(metadata)
        logging.info(display_description)

        coverage_store_info = gs_rest_api_coveragestores.CoverageStoreInfo(
            name=display_name, description=title,
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
            name=display_name, native_name=native_layer_name, title=title, srs=srs, metadata_links=metadata_link_entry, abstract=display_description)
        coverage_info.dimensions = dimensions
        coverage_info.supported_formats = {'string': ['GEOTIFF']}
        coverage_info.native_format = 'GEOTIFF'
        coverage_info.request_srs = {"string": ["EPSG: 4326"]}
        coverage_info.response_srs = {"string": ["EPSG: 4326"]}
        coverage_info.interpolation_methods = {"string": ["nearest neighbor"]}
        coverage_info.default_interpolation_method = {
            "string": ["nearest neighbor"]}
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
                "The input params were native_layer_name: {} display_name: {} title: {} url_location: {} srs: {} metadata: {}".format(
                    native_layer_name, display_name, title, url_location, srs, metadata))

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

    raster_name_string = "{0}_OV"
    hillshade_name_string = "{0}_HS"

    raster_label_string = "{0} OV"
    hillshade_label_string = "{0} HS"

    def get_coverage_label_bathy(self, product_l3_dist: ProductL3Dist):
        return self.product_database.get_label_for_product(
            product_l3_dist, self.raster_label_string)

    def get_coverage_label_hillshade(self, product_l3_dist: ProductL3Dist):
        return self.product_database.get_label_for_product(
            product_l3_dist, self.hillshade_label_string)

    def get_coverage_name_bathy(self, product_l3_dist: ProductL3Dist):
        return self.product_database.get_name_for_product(
            product_l3_dist, self.raster_name_string)

    def get_coverage_name_hillshade(self, product_l3_dist: ProductL3Dist):
        return self.product_database.get_name_for_product(
            product_l3_dist, self.hillshade_name_string)

    def run(self):

        existing_rasters = self.get_coverages()
        logging.info("Found existing rasters {}".format(existing_rasters))

        raster_dimensions = {'coverageDimension': [
            {
                'name': 'Elevation',
                        'description': 'Elevation in metres'
            }
        ]
        }
        hillshade_dimensions = {'coverageDimension': [
            {
                'name': 'Shaded relief',
                        'description': 'created with gdaldem hillshade -az 30 -alt 45 -s 2'
            }
        ]
        }

        published_records = []
        # First worry about bathymetry, then hillshade
        for product_record in self.product_database.l3_products:
            bath_name = self.get_coverage_name_bathy(product_record)
            bath_label_name = self.get_coverage_label_bathy(product_record)

            if bath_name in published_records:
                logging.error(
                    "Duplicate coverage name {}".format(bath_name))
                continue
            published_records.append(bath_name)

            # Add bathymetry Raster
            if bath_name in existing_rasters:
                logging.info("Already have raster coveragestore: {}".format(
                    bath_name))
            else:
                self.create_raster(
                    bath_name, bath_label_name,
                    product_record.bathymetry_location, product_record.source_product.srs,
                    product_record.source_product.metadata_persistent_id, raster_dimensions)

            hillshade_name = self.get_coverage_name_hillshade(product_record)
            hillshade_label = self.get_coverage_label_hillshade(product_record)

            if product_record.hillshade_location == "":
                logging.info("No hillshade raster defined for: {}".format(
                    hillshade_name))
            elif hillshade_name in existing_rasters:
                logging.info("Already have raster coveragestore: {}".format(
                    hillshade_name))
            else:
                self.create_raster(
                    hillshade_name, hillshade_label,
                    product_record.hillshade_location, product_record.source_product.srs,
                    product_record.source_product.metadata_persistent_id, hillshade_dimensions)
