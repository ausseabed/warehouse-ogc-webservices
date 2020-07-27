import gs_rest_api_layergroups
from gs_rest_api_layergroups.rest import ApiException
from gs_rest_api_layergroups import LayergroupResponse
from gs_rest_api_layergroups import LayergroupPublished
from gs_rest_api_layergroups import LayergroupWrapper
from gs_rest_api_layergroups import LayergroupStyle

from style_add_task import StyleAddTask

import os
import sys
import logging

import gs_rest_api_coverages
from gs_rest_api_coverages.rest import ApiException
from gs_rest_api_coverages import CoverageInfoWrapper
from gs_rest_api_coverages import CoverageInfo

from urllib.parse import quote_plus

from typing import List
from product_database import ProductDatabase
from raster_add_task import RasterAddTask
from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, SurveyL3Relation, Survey


class GroupLayerTask(object):

    def __init__(self, configuration, workspace_name, product_database: ProductDatabase):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_database = product_database

    def get_coverage_info(self, coverage_name):
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_coverages.DefaultApi(
            gs_rest_api_coverages.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get a list of all coverage stores in {workspace}
            api_response = api_instance.get_coverage(
                self.workspace_name, coverage_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_coverage: %s\n" % e)
            raise

        return api_response['coverage']

    def get_bounding_box(self, layer_name):
        logging.info(
            "Finding bounding box for {}".format(layer_name))
        try:
            layer = self.get_coverage_info(layer_name)
        except ApiException as e:
            logging.error("Can't get bounding box: %s\n" % e)
            raise

        bbox = layer["nativeBoundingBox"]
        srs = layer["srs"]

        # want form ("433248.5", "5662267.5", "455227.5", "5677920.5", "EPSG:28355")
        # have form {u'minx': 146.82151735057383, u'miny': -39.47860797949455, u'maxx': 147.48124691203017, u'maxy': -39.223417842248914, u'crs': u'EPSG:4326'}
        bbox_output = (bbox[u'minx'], bbox[u'maxx'],
                       bbox[u'miny'], bbox[u'maxy'], srs)
        bbox["crs"] = srs
        logging.info(str(bbox))
        return bbox

    def create_layer_link(self, layer_name):
        url = '{server_url}/workspaces/{workspace_name}/layers/{layer_name}.xml'.format(
            server_url=self.configuration.host, workspace_name=quote_plus(self.workspace_name), layer_name=quote_plus(layer_name))
        l = LayergroupPublished(name="{}:{}".format(
            self.workspace_name, layer_name), link=url, type="layer")
        logging.info("Created layer link: {}".format(layer_name))
        return l

    def create_style_link(self, style_name):
        style_url = '{server_url}/workspaces/{workspace_name}/styles/{style_name}.xml'.format(
            server_url=self.configuration.host, workspace_name=quote_plus(self.workspace_name), style_name=quote_plus(style_name))
        l = LayergroupStyle(name="{}:{}".format(
            self.workspace_name, style_name), link=style_url)
        logging.info("Created layer link: {}".format(style_name))
        return l

    def create_group_layers(self, group_layer_name, group_layer_label, list_of_layers, list_of_styles, bbox, metadata_url):
        logging.info(
            "Creating group layer {}".format(group_layer_name))

        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_client = gs_rest_api_layergroups.ApiClient(
            self.configuration, header_name='Authorization', header_value=authtoken)

        api_instance = gs_rest_api_layergroups.DefaultApi(api_client)

        abstract = RasterAddTask.get_abstract(metadata_url)

        # Layergroup | The layer group body information to upload.
        layergroup = gs_rest_api_layergroups.Layergroup(
            name=group_layer_name, workspace=self.workspace_name, title=group_layer_label, bounds=bbox, abstract_txt=abstract)
        layergroup.publishables = {'published': [self.create_layer_link(
            layer) for layer in list_of_layers]}

        # layergroup.styles = {'style': [
        #    self.create_style_link(style_name) for style_name in list_of_styles]}

        layer_group_wrapper = LayergroupWrapper(layergroup)
        try:
            # Add a new layer group
            api_response = api_instance.post_workspace_layergroups(
                layer_group_wrapper, self.workspace_name)
        except Exception as e:
            logging.error(
                "Exception when calling DefaultApi->post_workspace_layergroups: %s\n" % e)

    def get_layer_groups(self):
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_layergroups.DefaultApi(
            gs_rest_api_layergroups.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get a list of all coverage stores in {workspace}
            api_response = api_instance.get_workspace_layergroups(
                self.workspace_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_coverage_stores: %s\n" % e)

        if isinstance(api_response, LayergroupResponse):
            if api_response.layer_groups == '':
                layer_names = []
            else:
                layer_names = [layer_names['name']
                               for layer_names in api_response.layer_groups['layerGroup']]
        else:
            layer_names = []

        return layer_names

    group_layer_presentation_string = "{0}"

    def merge_bbox(self, list_bboxes, group_layer_name):
        crc_to_bboxes = {}
        for bbox in list_bboxes:
            crc_to_bboxes.setdefault(bbox['crs'], []).append(bbox)
        if len(crc_to_bboxes.keys()) == 0:
            logging.error("No bounding boxes found for " + group_layer_name)
            return None

        if len(crc_to_bboxes.keys()) > 1:
            logging.warn('Multiple CRCs found for ' +
                         group_layer_name + '. Bounds will be incorrectly set. Crcs: ' + str(crc_to_bboxes.keys()))

        max_bboxes = max([len(value_list)
                          for (crc, value_list) in crc_to_bboxes.items()])

        for (crc_key, values) in crc_to_bboxes.items():
            if len(values) == max_bboxes:
                selected_list_bboxes = crc_to_bboxes[crc_key]
                crc = crc_key
                break

        bbox = {
            'minx': min([x["minx"] for x in selected_list_bboxes]),
            'maxx': max([x["maxx"] for x in selected_list_bboxes]),
            'miny': min([x["miny"] for x in selected_list_bboxes]),
            'maxy': max([x["maxy"] for x in selected_list_bboxes]),
            'crs': crc
        }
        return bbox

    def merge_metadata_urls(self, list_metadata_urls):
        for url in list_metadata_urls:
            if (url != ""):
                return url
        return ""

    def run(self):

        existing_layer_groups = self.get_layer_groups()
        logging.info("Found existing layer groups {}".format(
            existing_layer_groups))

        published_records = []

        # Collate by survey - year - resolution
        set_of_survey_names = self.product_database.get_survey_names()

        for (group_layer_name, group_layer_label) in set_of_survey_names:
            # logging.info("Group " + group_layer_name)
            if group_layer_name in existing_layer_groups:
                logging.warn("Already have group layer for {}".format(
                    group_layer_name))
                continue

            product_records = self.product_database.get_products_for_survey_name(
                group_layer_label)

            bboxes = []
            metadata_urls = []
            error_free_product_records = []
            error_free_product_styles = []
            for product_record in product_records:
                bath_display_name = self.product_database.get_name_for_product(
                    product_record, RasterAddTask.raster_name_string)
                # logging.info("Layer " + bath_display_name)
                hs_display_name = self.product_database.get_name_for_product(
                    product_record, RasterAddTask.hillshade_name_string)

                if bath_display_name in published_records:
                    logging.error(
                        "Duplicate coverage name {}".format(bath_display_name))
                    continue

                if product_record.hillshade_location == "":
                    logging.warn("No hillshade raster defined for: {}".format(
                        hs_display_name))
                    continue
                try:
                    bbox = self.get_bounding_box(bath_display_name)
                    metadata_url = product_record.source_product.metadata_persistent_id
                    bboxes.append(bbox)
                    metadata_urls.append(metadata_url)
                except ApiException as e:
                    logging.error("Can't create layer %s\n" % e)
                error_free_product_records.append(hs_display_name)
                error_free_product_records.append(bath_display_name)
                error_free_product_styles.append(
                    StyleAddTask.BATH_HILLSHADE_STYLE_NAME)
                error_free_product_styles.append(StyleAddTask.BATH_STYLE_NAME)
            if (len(error_free_product_records) == 0):
                logging.error("No records for group layer " +
                              group_layer_label)
                continue
            try:
                bbox = self.merge_bbox(bboxes, group_layer_label)
                metadata_url = self.merge_metadata_urls(metadata_urls)
                self.create_group_layers(group_layer_name, group_layer_label,
                                         error_free_product_records,
                                         error_free_product_styles,
                                         bbox, metadata_url)
            except ApiException as e:
                logging.error("Can't create layer %s\n" % e)

        # For backwards compatibility
        published_records = []
        for product_record in self.product_database.l3_dist_products:
            group_layer_name = self.product_database.get_name_for_product(
                product_record, self.group_layer_presentation_string)

            group_layer_label = self.product_database.get_label_for_product(
                product_record, self.group_layer_presentation_string)

            bath_display_name = self.product_database.get_name_for_product(
                product_record, RasterAddTask.raster_name_string)

            hs_display_name = self.product_database.get_name_for_product(
                product_record, RasterAddTask.hillshade_name_string)

            if bath_display_name in published_records:
                logging.error(
                    "Duplicate coverage name {}".format(bath_display_name))
                continue
            published_records.append(bath_display_name)

            if product_record.hillshade_location == "":
                logging.info("No hillshade raster defined for: {}".format(
                    hs_display_name))
            elif group_layer_name in existing_layer_groups:
                logging.info("Already have group layer for {}".format(
                    bath_display_name))
            else:
                try:
                    bbox = self.get_bounding_box(
                        bath_display_name)
                    metadata_url = product_record.source_product.metadata_persistent_id
                    self.create_group_layers(group_layer_name, group_layer_label,
                                             [hs_display_name,
                                              bath_display_name],
                                             [StyleAddTask.BATH_HILLSHADE_STYLE_NAME,
                                                 StyleAddTask.BATH_STYLE_NAME],
                                             bbox, metadata_url
                                             )
                except ApiException as e:
                    logging.error("Can't create layer %s\n" % e)
