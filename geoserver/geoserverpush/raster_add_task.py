import gs_rest_api_coveragestores
from gs_rest_api_coveragestores.rest import ApiException
from gs_rest_api_coveragestores.model.coverage_store_info import CoverageStoreInfo
from gs_rest_api_coveragestores.model.coverage_store_info_wrapper import CoverageStoreInfoWrapper
import gs_rest_api_coverages
from gs_rest_api_coverages.rest import ApiException
from gs_rest_api_coverages.model.coverage_info import CoverageInfo
from gs_rest_api_coverages.model.coverage_info_wrapper import CoverageInfoWrapper

from pprint import pprint

import os
import sys
import logging
from product_record import ProductRecord
from typing import List


class RasterAddTask(object):

    def __init__(self, configuration, workspace_name, product_records: List[ProductRecord]):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_records = product_records

    def create_raster(self, native_layer_name, display_name, display_description, url_location, srs, metadata):

        logging.info(
            "Creating coveragestore for raster {}".format(display_name))
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
        api_instance = gs_rest_api_coveragestores.DefaultApi(api_client)

        try:
            api_instance.post_coverage_stores(
                coverage_store_info_wrapper, self.workspace_name)
        except ApiException as e:
            print(
                "Exception when calling DefaultApi->post_coverage_store_upload: %s\n" % e)

        # create an instance of the API class
        api_instance = gs_rest_api_coverages.DefaultApi(
            gs_rest_api_coverages.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))
        # CoverageInfo | The body of the coverage to POST
        coverage_info = gs_rest_api_coverages.CoverageInfo(
            name=display_name, native_name=native_layer_name, title=display_name, srs=srs, metadata=metadata)
        # data = "<coverage><name>{}</name><title>{}</title><nativeName>{}</nativeName><srs>{}</srs></coverage>".format(
        #    display_name, display_name, native_layer_name, srs)
        workspace = self.workspace_name  # str | The name of the workspace
        store = display_name  # str | The name of the coverage data store

        body = gs_rest_api_coverages.CoverageInfoWrapper(coverage_info)
        try:
            api_instance.post_workspace_coverage_store(body, workspace, store)
        except ApiException as e:
            print(
                "Exception when calling DefaultApi->post_workspace_coverage_store: %s\n" % e)

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

    def run(self):

        existing_rasters = self.get_coverages()
        logging.info("Found existing rasters {}".format(existing_rasters))

        # First worry about bathymetry, then hillshade
        for product_record in self.product_records:
            geoserver_bath_raster = product_record.get_bathymetric_raster()
            self.create_raster(geoserver_bath_raster.native_layer_name,
                               geoserver_bath_raster.display_name, geoserver_bath_raster.display_name,
                               geoserver_bath_raster.source_tif, geoserver_bath_raster.srs, geoserver_bath_raster.metadata)

            # coverage_name = product_record.get_l0_coverage_name()
            # shapefile = product_record.get_l0_coverage()
            # if shapefile == '':
            #     logging.info(
            #         "Skipping coverage because there is no file: {}".format(coverage_name))
            # elif coverage_name in existing_datastores:
            #     logging.info("Already have coverage: {}".format(coverage_name))
            # else:
            #     self.create_coverage(product_record
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
