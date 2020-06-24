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


class CoverageAddTask(object):

    def __init__(self, configuration, workspace_name, product_database: ProductDatabase):
        self.configuration = configuration
        self.workspace_name = workspace_name
        self.product_database = product_database

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
    def shapefile_plus_sidecars(self, path):
        return {ext: path + "." + ext for ext in ['shx', 'shp', 'dbf', 'prj']}

    def create_shapefile_zip(self, shapefile_url, shapefile_display_name):
        # 1. create a temp directory
        base_dir = self.create_temp_dir()
        shapefile_name = re.sub(".*/", "", shapefile_url)
        polygon_dest = base_dir + "/" + shapefile_name

        source_shapefile_plus_sidecars = self.shapefile_plus_sidecars(
            shapefile_url.replace(".shp", ""))
        shapefile_plus_sidecars = self.shapefile_plus_sidecars(
            polygon_dest.replace(".shp", ""))

        shapefile_name_plus_sidecars = self.shapefile_plus_sidecars(
            shapefile_display_name)
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

    def create_coverage(self, coverage_location, coverage_name):
        logging.info("Creating datastore {}".format(coverage_name))

        zip_coverage = self.create_shapefile_zip(
            coverage_location, coverage_name)

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

    def get_existing_datastores(self):
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_datastores.DefaultApi(
            gs_rest_api_datastores.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get a list of data stores
            api_response = api_instance.get_datastores(self.workspace_name)
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

    def run(self):
        existing_datastores = self.get_existing_datastores()
        logging.info("Found existing datastores {}".format(
            existing_datastores))

        published_records = []
        for product_record in self.product_database.l3_products:
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
                    self.create_coverage(
                        product_record.l3_coverage_location, coverage_name)
                    self.update_layer_name(coverage_name, coverage_label)
                except subprocess.CalledProcessError:
                    logging.error(
                        "Could not copy shapefile: {}".format(coverage_name))
