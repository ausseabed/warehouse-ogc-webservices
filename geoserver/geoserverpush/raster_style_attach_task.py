import gs_rest_api_layers
from gs_rest_api_layers.rest import ApiException
from gs_rest_api_layers import Layers
from gs_rest_api_layers import LayerWrapper
from gs_rest_api_layers import Layer
from gs_rest_api_layers import StyleReference

import os
import sys
import logging
from product_record import ProductRecord
from typing import List
from style_add_task import StyleAddTask


class RasterStyleAttachTask(object):

    def __init__(self, configuration, workspace_name, product_records: List[ProductRecord]):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_records = product_records

    def get_layer(self, layer_name) -> LayerWrapper:
        logging.info("Getting layer {}".format(layer_name))
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_layers.DefaultApi(
            gs_rest_api_layers.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get a list of all coverage stores in {workspace}
            api_response = api_instance.layers_name_workspace_get(
                self.workspace_name, layer_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->layers_workspace_get: %s\n" % e)

        return api_response

    def attach_style(self, display_name, style_name, style_ref=""):

        logging.info(
            "Attaching style for raster {}".format(display_name))

        authtoken = self.configuration.get_basic_auth_token()

        api_client = gs_rest_api_layers.ApiClient(
            self.configuration, header_name='Authorization', header_value=authtoken)

        # create an instance of the API class
        api_instance = gs_rest_api_layers.DefaultApi(api_client)

        # Layer | The updated layer definition.
        layer_wrapper = self.get_layer(display_name)
        layer = layer_wrapper.layer
        style_ref = StyleReference(style_name, style_ref)
        layer.default_style = style_ref
        # Object | The name of the workspace the layer is in.
        workspace_name = self.workspace_name
        layer_name = display_name  # str | The name of the layer to modify.

        try:
            # Modify a layer.
            api_instance.layers_name_workspace_put(
                layer_wrapper, self.workspace_name, display_name)
        except ApiException as e:
            print(
                "Exception when calling DefaultApi->layers_name_workspace_put: %s\n" % e)
        # authtoken = self.configuration.get_basic_auth_token()
        # # create an instance of the API class
        # api_client = gs_rest_api_coveragestores.ApiClient(
        #     self.configuration, header_name='Authorization', header_value=authtoken)

        # # NOTE for non-public services, we will have some work to do here
        # url = url_location + \
        #     "?useAnon=true&awsRegion=AP_SOUTHEAST_2"  # ap-southeast-2

        # coverage_store_info = gs_rest_api_coveragestores.CoverageStoreInfo(
        #     name=display_name, description=display_description,
        #     type="S3GeoTiff", workspace=self.workspace_name, enabled=True,
        #     url=url)

        # coverage_store_info_wrapper = gs_rest_api_coveragestores.CoverageStoreInfoWrapper(
        #     coverage_store=coverage_store_info)

        # # create an instance of the API class
        # cs_api_instance = gs_rest_api_coveragestores.DefaultApi(api_client)

        # try:
        #     cs_api_instance.post_coverage_stores(
        #         coverage_store_info_wrapper, self.workspace_name)
        # except ApiException as e:
        #     logging.error(
        #         "Exception when calling DefaultApi->post_coverage_store_upload: %s\n" % e)
        #     return

        # # create an instance of the API class
        # api_instance = gs_rest_api_coverages.DefaultApi(
        #     gs_rest_api_coverages.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))
        # # CoverageInfo | The body of the coverage to POST
        # coverage_info = gs_rest_api_coverages.CoverageInfo(
        #     name=display_name, native_name=native_layer_name, title=display_name, srs=srs, metadata=metadata)
        # # data = "<coverage><name>{}</name><title>{}</title><nativeName>{}</nativeName><srs>{}</srs></coverage>".format(
        # #    display_name, display_name, native_layer_name, srs)
        # workspace = self.workspace_name  # str | The name of the workspace
        # store = display_name  # str | The name of the coverage data store

        # body = gs_rest_api_coverages.CoverageInfoWrapper(coverage_info)
        # try:
        #     api_instance.post_workspace_coverage_store(body, workspace, store)
        # except ApiException as e:
        #     logging.error(
        #         "Exception when calling DefaultApi->post_workspace_coverage_store: %s\n" % e)
        #     logging.error(
        #         "Please manually remove coverage store {} before next attempt to submit".format(display_name))
        #     logging.error(
        #         "The input params were native_layer_name: {} display_name: {} display_description: {} url_location: {} srs: {} metadata: {}".format(
        #             native_layer_name, display_name, display_description, url_location, srs, metadata))

    def get_layers(self):
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_layers.DefaultApi(
            gs_rest_api_layers.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get a list of all coverage stores in {workspace}
            api_response = api_instance.layers_workspace_get(
                self.workspace_name)
            logging.info(api_response)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->layers_workspace_get: %s\n" % e)

        if not(isinstance(api_response, Layers)):
            layer_names = []
        else:
            layer_names = [layer_names['name']
                           for layer_names in api_response.layers['layer']]

        return layer_names

    def run(self):

        existing_layers = self.get_layers()
        logging.info(
            "Found existing layer definitions {}".format(existing_layers))

        # First worry about bathymetry, then hillshade
        for product_record in self.product_records:
            geoserver_bath_raster = product_record.get_bathymetric_raster()
            # Add bathymetry Raster
            if geoserver_bath_raster.display_name in existing_layers:
                self.attach_style(
                    geoserver_bath_raster.display_name, StyleAddTask.BATH_HILLSHADE_STYLE_NAME)
            else:
                logging.warn("Cannot find layer for raster: {}".format(
                    geoserver_bath_raster.display_name))

            geoserver_hs_raster = product_record.get_hillshade_raster()
            if geoserver_hs_raster.display_name in existing_layers:
                self.attach_style(
                    geoserver_hs_raster.display_name, StyleAddTask.BATH_STYLE_NAME)
            else:
                logging.info("Cannot find layer for raster: {}".format(
                    geoserver_hs_raster.display_name))

        #     geoserver_catalog_services.add_style_to_raster(geoserver_bath_raster_ref["name"],
        #                                                    geoserver_catalog_services.BATH_STYLE_NAME)
        #         geoserver_catalog_services.add_style_to_raster(geoserver_hs_raster_ref["name"],
        #                                                        geoserver_catalog_services.BATH_HILLSHADE_STYLE_NAME)
        #         geoserver_catalog_services.group_layers(
        #             [geoserver_hs_raster, geoserver_bath_raster],
        #             [geoserver_catalog_services.BATH_HILLSHADE_STYLE_NAME,
        #                 geoserver_catalog_services.BATH_STYLE_NAME],
        #             geoserver_hs_raster_ref["bbox"]
        #         )
