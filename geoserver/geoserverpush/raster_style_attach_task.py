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
from urllib.parse import quote_plus

from product_record import ProductRecord
from typing import List
from product_database import ProductDatabase

from raster_add_task import RasterAddTask

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, SurveyL3Relation, Survey


class RasterStyleAttachTask(object):

    def __init__(self, configuration, workspace_name, product_database: ProductDatabase):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_database = product_database
        self.server_url = configuration.host

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

    def attach_style(self, display_name, style_name):

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

        style_url = '{server_url}/workspaces/{workspace_name}/styles/{style_name}.xml'.format(
            server_url=self.server_url, workspace_name=quote_plus(self.workspace_name), style_name=quote_plus(style_name))
        style_ref = StyleReference(style_name, style_url)
        logging.info("Creating ref to schema {}, url: {}".format(
                     style_name, style_ref))
        layer.default_style = style_ref

        try:
            # Modify a layer.
            api_instance.layers_name_workspace_put(
                layer_wrapper, self.workspace_name, display_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->layers_name_workspace_put: %s\n" % e)

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

        published_records = []
        # First worry about bathymetry, then hillshade
        for product_record in self.product_database.l3_products:

            bath_display_name = self.product_database.get_name_for_product(
                product_record, RasterAddTask.raster_presentation_string)

            if bath_display_name in published_records:
                logging.error(
                    "Duplicate coverage name {}".format(bath_display_name))
                continue
            published_records.append(bath_display_name)

            # Add bathymetry Raster
            if bath_display_name in existing_layers:
                self.attach_style(
                    bath_display_name, StyleAddTask.BATH_STYLE_NAME)
            else:
                logging.warn("Cannot find layer for raster: {}".format(
                    bath_display_name))

            hs_display_name = self.product_database.get_name_for_product(
                product_record, RasterAddTask.hillshade_presentation_string)
            if hs_display_name in existing_layers:
                self.attach_style(
                    hs_display_name, StyleAddTask.BATH_HILLSHADE_STYLE_NAME)
            else:
                logging.info("Cannot find layer for raster: {}".format(
                    hs_display_name))
