import logging

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey
from src_dist_name import SrcDistName
import product_catalogue_py_rest_client
from product_catalogue_py_rest_client.rest import ApiException
import re


class UpdateDatabaseAction():

    def __init__(self, product_l3_src: ProductL3Src, database_url, token):
        self.product_l3_src = product_l3_src
        self.src_dist_name = SrcDistName(product_l3_src)
        self.database_url = database_url
        self.token = token

    def update(self):
        configuration = product_catalogue_py_rest_client.Configuration(
            host=self.database_url
        )
        configuration.access_token = self.token
        # Enter a context with an instance of the API client
        with product_catalogue_py_rest_client.ApiClient(configuration) as api_client:
            # Create an instance of the API class
            api_instance = product_catalogue_py_rest_client.ProductsL3DistApi(
                api_client)
            product_l3_src_id = self.product_l3_src.id
            product_l3_dist_dto = product_catalogue_py_rest_client.ProductL3DistDto(
                bathymetry_location=self.src_dist_name.s3_dest_tif,
                hillshade_location=self.src_dist_name.s3_hillshade_dest_tif,
                l3_coverage_location=self.src_dist_name.s3_dest_shp
            )

        try:
            api_response = api_instance.products_l3_dist_controller_create(
                product_l3_src_id, product_l3_dist_dto)
            logging.info(api_response)
        except ApiException as e:
            logging.error(
                "Exception when calling ProductsL3DistApi->products_l3_dist_controller_create: %s\n" % e)
