import logging
import math
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from typing import List
from xml.sax.saxutils import escape

import product_catalogue_py_rest_client
from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey
from product_catalogue_py_rest_client.rest import ApiException


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

    def __init__(self, bearer_id, database_url=""):
        self.resolution_regex = re.compile(r"^(?P<min>\d*\.?\d+)m?(?:.*?)?(?P<max>\d*\.?\d+)?m?$")
        self.bearer_id = bearer_id
        self.source_tif_path = database_url
        self.snapshot_iso_datetime = str(
            datetime.utcnow().isoformat())

    def load_from_commandline(self):
        try:
            self.source_tif_path = os.environ['LIST_PATH']
        except KeyError:
            logging.exception("Please set the environment variable LIST_PATH")
            sys.exit(1)

        logging.info("Path to file that specifies what to load (LIST_PATH) = " +
                     self.source_tif_path)

        try:
            self.snapshot_iso_datetime = os.environ['SNAPSHOT_ISO_DATETIME']
        except KeyError:
            logging.warning(
                "Please set the environment variable SNAPSHOT_ISO_DATETIME. Using: " + self.snapshot_iso_datetime)

        logging.info("Using SNAPSHOT_ISO_DATETIME = " +
                     self.snapshot_iso_datetime)

    def download_from_rest(self):
        self.l3_dist_products = self.retrieve_l3_products_using_rest()
        self.l3_src_products = self.retrieve_l3_src_products_using_rest()
        self.survey_l3_relations = self.retrieve_survey_l3_relations()
        self.surveys = self.retrieve_surveys()
        self.remove_orphans()
        self.remove_msl_when_ellipsoid()
        self.create_label_base_name()
        self.create_raster_base_name()
        self.create_survey_label_base_name()
        self.create_survey_raster_base_name()
        self.create_survey_zip_name()
        self.remove_orphans()

    """ If there is a record with ellipsoid in a survey, only
    allow products with an ellipsoid
    """

    def remove_msl_when_ellipsoid(self):
        self.ellipsoid_parents = set([z.id for x in self.l3_src_products
                                      for y in self.survey_l3_relations
                                      for z in self.surveys
                                      if x.id == y.product_id and y.survey_id == z.id
                                      and x.vertical_datum == 'WGS84'])

        self.l3_dist_products_filtered = [l3_dist_product for l3_dist_product in self.l3_dist_products
                                          for relation in self.survey_l3_relations
                                          if relation.product_id == l3_dist_product.source_product.id and
                                          (l3_dist_product.source_product.vertical_datum == 'WGS84' or
                                           relation.survey_id not in self.ellipsoid_parents)
                                          ]

        removed = set([x.source_product.name for x in self.l3_dist_products]).difference(
            set([x.source_product.name for x in self.l3_dist_products_filtered]))

        logging.info(
            "Removing MSL products in surveys with Ellipsoid products: " + str(removed))

        self.l3_dist_products = self.l3_dist_products_filtered

    def remove_orphans(self):
        src_prods = [x for x in self.l3_src_products
                     for y in self.survey_l3_relations
                     for z in self.surveys
                     if x.id == y.product_id and y.survey_id == z.id]

        src_product_ids = list(map(lambda x: x.id, src_prods))

        unmatched = [
            x.source_product.name for x in self.l3_dist_products if x.source_product.id not in src_product_ids]
        if (len(unmatched) > 0):
            logging.error("Orphaned surveys: {}".format(", ".join(unmatched)))
        matched = [
            x for x in self.l3_dist_products if x.source_product.id in src_product_ids]
        self.l3_dist_products = matched

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

    def retrieve_l3_products_using_rest(self) -> List[ProductL3Dist]:
        configuration = product_catalogue_py_rest_client.Configuration(
            host=self.source_tif_path
        )
        configuration.access_token = self.bearer_id
        with product_catalogue_py_rest_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = product_catalogue_py_rest_client.ProductsL3DistApi(
                api_client)

            try:
                api_response = api_instance.products_l3_dist_controller_find_all(
                    snapshot_date_time=self.snapshot_iso_datetime)
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
                api_response = api_instance.product_relations_controller_find_all_l3_survey(
                    snapshot_date_time=self.snapshot_iso_datetime)
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
                api_response = api_instance.surveys_controller_find_all(
                    snapshot_date_time=self.snapshot_iso_datetime)
                # logging.info(api_response)
                return api_response
            except ApiException as e:
                logging.error(
                    "Exception when calling CompilationsApi->compilations_controller_create: %s\n" % e)

    # https://www.w3.org/TR/1999/REC-xml-names-19990114/#NT-NCName defines the values allowable in a NCName (used in GML)
    # See NGA-366 - also removing .
    # NCName = [\i-[:]][\c-[:]]*
    SLASH_I_LESS_COLON = "A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD"
    SLASH_C_LESS_COLON = "-0-9A-Z_a-z\u00B7\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u037D\u037F-\u1FFF\u200C-\u200D\u203F\u2040\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD"

    def create_raster_base_name(self):
        self.base_names = {x_id: re.sub("^[^"+self.SLASH_I_LESS_COLON+"]", "_", re.sub("[^"+self.SLASH_C_LESS_COLON+"]", "_", x_name))
                           for (x_id, x_name) in self.base_label_names.items()}

    def create_label_base_name(self):
        self.base_label_names = {x.id: "{0} {1} {2}".format(x.name, z.year, x.resolution)
                                 for x in self.l3_src_products
                                 for y in self.survey_l3_relations
                                 for z in self.surveys
                                 if x.id == y.product_id and y.survey_id == z.id}

    def create_survey_raster_base_name(self):
        self.survey_base_names = {x_id: re.sub("^[^"+self.SLASH_I_LESS_COLON+"]", "_", re.sub("[^"+self.SLASH_C_LESS_COLON+"]", "_", x_name))
                                  for (x_id, x_name) in self.survey_base_label_names.items()}

    def create_survey_label_base_name(self):
        self.survey_base_label_names = {x.id: "{0} {1} {2}".format(z.name, z.year, x.resolution)
                                        for x in self.l3_src_products
                                        for y in self.survey_l3_relations
                                        for z in self.surveys
                                        if x.id == y.product_id and y.survey_id == z.id}

    def create_survey_zip_name(self):
        self.survey_zip_names = {}

        products = dict(map(lambda product: (product.id, product), self.l3_src_products))
        survey_to_products = defaultdict(list)

        for relation in self.survey_l3_relations:
            survey_to_products[relation.survey_id].append(relation.product_id)

        for survey in self.surveys:
            if survey.id not in survey_to_products:
                logging.warning('No products for survey: %s', survey.id)
                continue

            resolutions = set()

            for product_id in survey_to_products[survey.id]:
                if product_id not in products:
                    logging.warning('Product %s does not exist for survey: %s', product_id, survey.id)
                    continue

                resolutions.add(products[product_id].resolution)

            resolution_text = self.extract_resolution_text(resolutions)
            zip_filename = f'{survey.name.strip()} {survey.year.strip()} {resolution_text}.zip'
            zip_filename = re.sub(r'[\\/:*?\"<>|]', '_', zip_filename)

            for product_id in survey_to_products[survey.id]:
                self.survey_zip_names[product_id] = zip_filename

    def extract_resolution_text(self, resolutions):
        min_resolution = math.inf
        max_resolution = -math.inf

        for resolution in resolutions:
            match = self.resolution_regex.match(resolution)
            if match:
                min_resolution = min(min_resolution, float(match['min']))
                if match['max']:
                    max_resolution = max(max_resolution, float(match['max']))

        if max_resolution > -math.inf and not math.isclose(min_resolution, max_resolution):
            return f'{self.format_resolution(min_resolution)}m - {self.format_resolution(max_resolution)}m'

        return f'{self.format_resolution(min_resolution)}m'

    def format_resolution(self, resolution):
        return '{:.1f}'.format(resolution).rstrip('0').rstrip('.')

    def get_survey_names(self):
        return set(zip(self.survey_base_names.values(), self.survey_base_label_names.values()))

    def get_product_ids_for_survey_name(self, survey_name):
        return [product_id for (product_id, s_name) in self.survey_base_label_names.items() if s_name == survey_name]

    def get_products_for_survey_name(self, survey_name):
        matching_ids = self.get_product_ids_for_survey_name(survey_name)
        return [product for product in self.l3_dist_products if product.source_product.id in matching_ids]

    def get_label_for_product(self, l3_product: ProductL3Dist, format_string):
        if not(l3_product in self.l3_dist_products):
            logging.error(
                "Expecting to match product {} with survey (label0)".format(l3_product.source_product.name))
        else:
            return self.get_label_for_product_src(l3_product.source_product, format_string)

    def get_name_for_product(self, l3_product: ProductL3Dist, format_string):
        if not(l3_product in self.l3_dist_products):
            logging.error(
                "Expecting to match product {} with survey (name0)".format(l3_product.source_product.name))
        else:
            return self.get_name_for_product_src(l3_product.source_product, format_string)

    def get_label_for_product_src(self, l3_product: ProductL3Src, format_string):
        if not(l3_product.id in self.base_label_names):
            logging.error(
                "Expecting to match product {} with survey (label1)".format(l3_product.name))
        else:
            return escape(format_string.format(self.base_label_names[l3_product.id]))

    def get_name_for_product_src(self, l3_product: ProductL3Src, format_string):
        if not(l3_product.id in self.base_names):
            logging.error(
                "Expecting to match product {} with survey (name1)".format(l3_product.name))
        else:
            return escape(format_string.format(self.base_names[l3_product.id]))
