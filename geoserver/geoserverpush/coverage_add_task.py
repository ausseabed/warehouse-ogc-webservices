import gs_rest_api_datastores
from gs_rest_api_datastores.rest import ApiException
import uuid
import re
from shlex import quote
import subprocess
import tempfile
import zipfile
import io
import os
import sys
import logging
from copy import copy
import urllib
import six
from six.moves import http_client as httplib
from typing import List
from product_database import ProductDatabase
import gs_rest_api_layers
from gs_rest_api_layers.rest import ApiException
import gs_rest_api_featuretypes
from gs_rest_api_featuretypes.rest import ApiException
from product_catalogue_py_rest_client.models import ProductL3Dist, SurveyL3Relation, Survey
from s3util import S3Util
import dbf
from s3util import S3Util
from dbf import DbfError

from style_add_task import StyleAddTask
import gs_rest_api_layers
from gs_rest_api_layers.rest import ApiException
from gs_rest_api_layers import Layers
from gs_rest_api_layers import LayerWrapper
from gs_rest_api_layers import Layer
from gs_rest_api_layers import StyleReference
from urllib.parse import quote_plus


class CoverageAddTask(object):

    def __init__(self, configuration, workspace_name, product_database: ProductDatabase, meta_cache):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_database = product_database
        self.server_url = configuration.host
        self.meta_cache = meta_cache

    def copy_shapefile_local(self, polygon_dest, shapefile_name):

        polygon_src = shapefile_name.replace("s3://", "/vsis3/")

        cmd = ["/usr/bin/ogr2ogr", "-f",
               "ESRI Shapefile", polygon_dest, polygon_src]
        logging.info(" ".join(cmd))
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            logging.error("Status : FAIL {}, {}".format(exc.returncode,
                                                        exc.output))
            exit(exc.returncode)

    def copy_s3_file_local(self, remote_file_name, local_file_name):
        cmd = ["aws", "s3", "cp", remote_file_name, local_file_name]
        logging.info(" ".join(cmd))
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            logging.error("Status : FAIL {}, {}".format(exc.returncode,
                                                        exc.output))
            raise

    def create_temp_dir(self):
        cwd = tempfile.gettempdir()
        logging.info("Using current dictory as base: {}".format(cwd))
        new_dir = cwd + "/" + str(uuid.uuid4())
        try:
            os.mkdir(new_dir)
        except OSError:
            logging.error("Creation of the directory %s failed" % new_dir)
        else:
            logging.info("Successfully created the directory %s " % new_dir)
        return(new_dir)

    # https://pypi.org/project/geoserver-restconfig/
    def shapefile_plus_sidecars(self, path, plus_index=False):
        if plus_index:
            return {ext: path + "." + ext for ext in ['shx', 'shp', 'dbf', 'prj', 'sbx', 'sbn']}
        else:
            return {ext: path + "." + ext for ext in ['shx', 'shp', 'dbf', 'prj']}

    def update_shapefile_attributes(self, shapefile_display_name, dbf_location, product_record):
        display_title = self.meta_cache.extract_title(
            product_record.source_product.metadata_persistent_id)
        if (display_title == ""):
            display_title = shapefile_display_name
        with dbf.Table(dbf_location) as db:
            db.add_fields(
                'BATHY_TYPE C(20); NAME C(255); START_DATE C(30); END_DATE C(30); VESSEL C(255); INSTRUMENT C(255); BATHY_URL C(255); META_URL C(255)')
            for record in db:
                dbf.write(record,
                          NAME=display_title,
                          BATHY_TYPE='Multibeam',
                          START_DATE=self.meta_cache.extract_start(
                              product_record.source_product.metadata_persistent_id),
                          END_DATE=self.meta_cache.extract_end(
                              product_record.source_product.metadata_persistent_id),
                          VESSEL=self.meta_cache.extract_vessel(
                              product_record.source_product.metadata_persistent_id),
                          INSTRUMENT=self.meta_cache.extract_instrument(
                              product_record.source_product.metadata_persistent_id),
                          BATHY_URL=S3Util.https_url(
                              product_record.bathymetry_location),
                          META_URL=product_record.source_product.metadata_persistent_id)

    def create_shapefile_zip(self, shapefile_url, shapefile_display_name, product_record=None):
        # 1. create a temp directory
        base_dir = self.create_temp_dir()
        shapefile_name = re.sub(".*/", "", shapefile_url)
        polygon_dest = base_dir + "/" + shapefile_name

        spatial_index = S3Util.s3_exists(shapefile_url.replace(".shp", ".sbx"))

        logging.info(shapefile_url + " has spatial index = " +
                     str(spatial_index))

        source_shapefile_plus_sidecars = self.shapefile_plus_sidecars(
            shapefile_url.replace(".shp", ""), spatial_index)
        shapefile_plus_sidecars = self.shapefile_plus_sidecars(
            polygon_dest.replace(".shp", ""), spatial_index)

        shapefile_name_plus_sidecars = self.shapefile_plus_sidecars(
            shapefile_display_name, spatial_index)
        # shapefile_and_friends should look on the filesystem to find a shapefile
        # and related files based on the base path passed in
        #
        # shapefile_plus_sidecars == {
        #    'shp': 'states.shp',
        #    'shx': 'states.shx',
        #    'prj': 'states.prj',
        #    'dbf': 'states.dbf'
        # }

        # 2. use boto/gdal to copy local
        for (source, destination) in zip(source_shapefile_plus_sidecars.values(), shapefile_plus_sidecars.values()):
            self.copy_s3_file_local(source, destination)

        if product_record != None:
            self.update_shapefile_attributes(shapefile_display_name,
                                             shapefile_plus_sidecars['dbf'], product_record)

        # 3. register in geoserver as below
        logging.info(shapefile_plus_sidecars)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for (local_file_name, destination_name) in zip(shapefile_plus_sidecars.values(), shapefile_name_plus_sidecars.values()):
                local_file_handle = open(local_file_name, mode='rb')
                data = local_file_handle.read()
                local_file_handle.close()
                zip_file.writestr(destination_name, data)

        return zip_buffer.getvalue()

    def create_coverage(self, coverage_location, coverage_name, product_record):
        logging.info("Creating datastore {}".format(coverage_name))

        zip_coverage = self.create_shapefile_zip(
            coverage_location, coverage_name, product_record)

        logging.info("Using filename {}".format(coverage_location))

        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        no_byte_debug_configuration = copy(self.configuration)

        # so we don't end up with bytes on the output stream
        no_byte_debug_configuration.debug = False
        api_client = gs_rest_api_datastores.ApiClient(
            no_byte_debug_configuration, header_name='Authorization', header_value=authtoken)

        # api_client.set_default_header('Content-Type', 'application/zip')
        api_instance = gs_rest_api_datastores.DefaultApi(api_client)

        method = 'file'  # str | The upload method. Can be \"url\", \"file\", \"external\". \"file\" uploads a file from a local source. The body of the request is the file itself. \"url\" uploads a file from an remote source. The body of the request is a URL pointing to the file to upload. This URL must be visible from the server. \"external\" uses an existing file on the server. The body of the request is the absolute path to the existing file.
        # str | The type of source data store (e.g., \"shp\").
        file_format = 'shp'
        # str | The filename parameter specifies the target file name for the file to be uploaded. This is important to avoid clashes with existing files. (optional)
        # filename = "file.zip"

        try:
            # Uploads files to the data store, creating it if necessary
            api_instance.put_data_store_upload(self.workspace_name, coverage_name, method, file_format,
                                               body=zip_coverage)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->put_data_store_upload: %s\n" % e)

    label_format_string = "{0} L0 Coverage"
    name_format_string = "{0}_L0_Coverage"

    def get_coverage_label(self, product_l3_dist: ProductL3Dist):
        # match on prod_id
        return (self.product_database.get_label_for_product(product_l3_dist, self.label_format_string))

    def get_coverage_name(self, product_l3_dist: ProductL3Dist):
        # match on prod_id
        return (self.product_database.get_name_for_product(product_l3_dist, self.name_format_string))

    @staticmethod
    def get_existing_datastores(configuration, workspace_name):
        # create an instance of the API class
        authtoken = configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_datastores.DefaultApi(
            gs_rest_api_datastores.ApiClient(configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get a list of data stores
            api_response = api_instance.get_datastores(workspace_name)
            logging.info(api_response)
        except ApiException as e:
            logging.exception(
                "Exception when calling DefaultApi->get_datastores: %s\n" % e)

        if api_response['dataStores'] == '':
            data_store_names = []
        else:
            data_store_names = [style_record['name']
                                for style_record in api_response['dataStores']['dataStore']]
        return data_store_names

    def update_layer_name(self, coverage_name, coverage_label):
        # find layer
        logging.info("Changing name for coverage: {}".format(
            coverage_name))
        urlencoded_coverage_name = re.sub(" ", "%20", coverage_label)
        logging.info("Changing name for coverage: {}".format(
            urlencoded_coverage_name))

        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()

        # create an instance of the API class
        api_instance = gs_rest_api_featuretypes.DefaultApi(
            gs_rest_api_featuretypes.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))
        try:
            api_response = api_instance.get_feature_type(
                self.workspace_name, coverage_name, coverage_name, quiet_on_not_found=True)
            logging.info(api_response)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_feature_type: %s\n" % e)
            return

        # Option 1: to change the feature type under the hood - requires updating the interface
        body = api_response
        body['featureType']['name'] = coverage_name
        body['featureType']['title'] = coverage_label
        # update layer
        try:
            api_instance.put_feature_type(
                body, self.workspace_name, coverage_name, coverage_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->put_feature_type: %s\n" % e)

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
            raise

        return api_response

    def attach_style(self, display_name, default_style_name, alternate_style_names=[]):

        logging.info(
            "Attaching style for raster {}".format(display_name))

        authtoken = self.configuration.get_basic_auth_token()

        api_client = gs_rest_api_layers.ApiClient(
            self.configuration, header_name='Authorization', header_value=authtoken)

        # create an instance of the API class
        api_instance = gs_rest_api_layers.DefaultApi(api_client)

        # Layer | The updated layer definition.
        try:
            layer_wrapper = self.get_layer(display_name)
        except ApiException as e:
            logging.error(
                "Exception when calling get_layer: %s\n" % e)
            return

        layer = layer_wrapper.layer

        style_url = '{server_url}/workspaces/{workspace_name}/styles/{style_name}.xml'.format(
            server_url=self.server_url, workspace_name=quote_plus(self.workspace_name), style_name=quote_plus(default_style_name))
        style_ref = StyleReference(default_style_name, style_url)
        logging.info("Creating ref to schema {}, url: {}".format(
                     default_style_name, style_ref))
        layer.default_style = style_ref

        layer_styles = [style_ref]

        for style_name in alternate_style_names:
            style_url = '{server_url}/workspaces/{workspace_name}/styles/{style_name}.xml'.format(
                server_url=self.server_url, workspace_name=quote_plus(self.workspace_name), style_name=quote_plus(style_name))
            style_ref = StyleReference(style_name, style_url)
            layer_styles.append(style_ref)

        layer.styles = {"style": layer_styles}
        try:
            # Modify a layer.
            api_instance.layers_name_workspace_put(
                layer_wrapper, self.workspace_name, display_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->layers_name_workspace_put: %s\n" % e)

    def add_holdings_layers(self, existing_datastores):
        # The layers that need to be added:
        holding_survey = 's3://ausseabed-public-warehouse-bathymetry/custom/83adda30-0374-40cd-a97b-29e21481f236/AusSeabed_Holdings_AusOnly.shp'
        holding_survey_name = 'ausseabed_bathymetry'
        holding_survey_description = 'AusSeabed Bathymetry Holdings'

        holding_compilation = 's3://ausseabed-public-warehouse-bathymetry/custom/85bab83c-9ef6-4e9f-b242-a72dcd00aadc/ga_holdings_compilations.shp'
        holding_compilation_name = 'ga_holdings_compilations'
        holding_compilation_description = 'AusSeabed Bathymetry Holdings (compilations)'

        if holding_survey_name not in existing_datastores:
            self.create_coverage(holding_survey, holding_survey_name, None)
            self.update_layer_name(holding_survey_name,
                                   holding_survey_description)
            self.attach_style(holding_survey_name, StyleAddTask.AUSSEABED_BATHY_HOLDINGS_PURPLE_NAME, [
                              StyleAddTask.AUSSEABED_BATHY_HOLDINGS_PURPLE_NAME, StyleAddTask.AUSSEABED_BATHY_HOLDINGS_BY_SOURCE_NAME, StyleAddTask.AUSSEABED_BATHY_WITH_DATA_ACCESS_NAME])

        if holding_compilation_name not in existing_datastores:
            self.create_coverage(holding_compilation,
                                 holding_compilation_name, None)
            self.update_layer_name(
                holding_compilation_name, holding_compilation_description)
            self.attach_style(holding_compilation_name, StyleAddTask.AUSSEABED_BATHY_HOLDINGS_PURPLE_NAME, [
                              StyleAddTask.AUSSEABED_BATHY_HOLDINGS_PURPLE_NAME])

    def run(self):
        existing_datastores = CoverageAddTask.get_existing_datastores(
            self.configuration, self.workspace_name)
        logging.info("Found existing datastores {}".format(
            existing_datastores))

        self.add_holdings_layers(existing_datastores)

        published_records = []
        for product_record in self.product_database.l3_dist_products:
            coverage_name = self.get_coverage_name(product_record)
            coverage_label = self.get_coverage_label(product_record)
            if coverage_name in published_records:
                logging.error(
                    "Duplicate coverage name {}".format(coverage_name))
                continue
            published_records.append(coverage_name)

            if product_record.l3_coverage_location == '':
                logging.info(
                    "Skipping coverage because there is no file: {}".format(coverage_name))
            elif coverage_name in existing_datastores:
                logging.info("Already have coverage: {}".format(coverage_name))
            else:
                try:
                    if (S3Util.s3_exists(product_record.l3_coverage_location)):
                        self.create_coverage(
                            product_record.l3_coverage_location, coverage_name, product_record)
                        self.update_layer_name(coverage_name, coverage_label)
                    else:
                        logging.error("Missing shapefile {} for {} ({})".format(
                            product_record.l3_coverage_location, coverage_name, product_record.id))
                except subprocess.CalledProcessError:
                    logging.error(
                        "Could not copy shapefile: {}".format(coverage_name))
                except DbfError:
                    logging.exception(
                        "Could not understand dbf associated with shapefile: {}".format(coverage_name))
                except:
                    logging.exception(
                        "Unknown error associated with shapefile: {}".format(coverage_name))
