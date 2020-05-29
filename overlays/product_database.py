import sys
import os
import requests
import logging
import product_catalogue_py_rest_client
from product_catalogue_py_rest_client.rest import ApiException
from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey
from typing import List
from xml.sax.saxutils import escape


class ProductDatabase():
    """
    Product Database data structure (at the moment a json formatted file that has the form:
 [
  {"l3ProductTifLocation": "s3://bucket-name/name-of-file.tif",
  "hillshadeLocation": "s3://bucket-name/name-of-file.tif",
  "l0CoverageLocation": "s3://bucket-name/name-of-file.shp"
  "gazeteerName":"e.g. Beagle Commonwealth Marine Reserve",
  "year":2018,
  "resolution":"1m",
  "UUID":"68f44afd-78d0-412f-bf9c-9c9fdbe43968"}, "metadataPersistentId":"",...
    """
    # l3_products : List[ProductL3Dist]
    # survey_l3_relations   : List[RelationSummaryDto]
    # surveys   : List[Survey]

    def __init__(self, bearer_id):
        self.bearer_id = bearer_id

    def load_from_commandline(self):
        try:
            self.source_tif_path = os.environ['LIST_PATH']
        except KeyError:
            logging.exception("Please set the environment variable LIST_PATH")
            sys.exit(1)

        logging.info("Path to file that specifies what to load (LIST_PATH) = " +
                     self.source_tif_path)

    def download_from_rest(self):
        self.l3_dist_products = self.retrieve_l3_dist_products_using_rest()
        self.l3_src_products = self.retrieve_l3_src_products_using_rest()
        self.survey_l3_relations = self.retrieve_survey_l3_relations()
        self.surveys = self.retrieve_surveys()

    def retrieve_l3_src_products_using_rest(self) -> List[ProductL3Src]:
        configuration = product_catalogue_py_rest_client.Configuration(
            host=self.source_tif_path
        )
        configuration.access_token = self.bearer_id
        with product_catalogue_py_rest_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = product_catalogue_py_rest_client.ProductsL3SrcApi(
                api_client)

            try:
                api_response = api_instance.products_l3_src_controller_find_all()
                # logging.info(api_response)
                return api_response
            except ApiException as e:
                logging.error(
                    "Exception when calling CompilationsApi->compilations_controller_create: %s\n" % e)

    def retrieve_l3_dist_products_using_rest(self) -> List[ProductL3Dist]:
        configuration = product_catalogue_py_rest_client.Configuration(
            host=self.source_tif_path
        )
        configuration.access_token = self.bearer_id
        with product_catalogue_py_rest_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = product_catalogue_py_rest_client.ProductsL3DistApi(
                api_client)

            try:
                api_response = api_instance.products_l3_dist_controller_find_all()
                # logging.info(api_response)
                return api_response
            except ApiException as e:
                logging.error(
                    "Exception when calling CompilationsApi->compilations_controller_create: %s\n" % e)

    def retrieve_survey_l3_relations(self) -> List[RelationSummaryDto]:
        configuration = product_catalogue_py_rest_client.Configuration(
            host=self.source_tif_path
        )
        configuration.access_token = self.bearer_id
        with product_catalogue_py_rest_client.ApiClient(configuration) as api_client:

            # Create an instance of the API class
            api_instance = product_catalogue_py_rest_client.ProductRelationsApi(
                api_client)

            try:
                api_response = api_instance.product_relations_controller_find_all_l3_survey()
                # logging.info(api_response)
                return api_response
            except ApiException as e:
                logging.error(
                    "Exception when calling CompilationsApi->compilations_controller_create: %s\n" % e)

    def retrieve_surveys(self) -> List[Survey]:
        configuration = product_catalogue_py_rest_client.Configuration(
            host=self.source_tif_path
        )
        configuration.access_token = self.bearer_id
        with product_catalogue_py_rest_client.ApiClient(configuration) as api_client:

            # Create an instance of the API class
            api_instance = product_catalogue_py_rest_client.SurveysApi(
                api_client)

            try:
                api_response = api_instance.surveys_controller_find_all()
                # logging.info(api_response)
                return api_response
            except ApiException as e:
                logging.error(
                    "Exception when calling CompilationsApi->compilations_controller_create: %s\n" % e)
