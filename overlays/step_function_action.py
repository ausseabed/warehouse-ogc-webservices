
import logging
from update_database_action import UpdateDatabaseAction

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey

import json
import re
from src_dist_name import SrcDistName
import boto3


class StepFunctionAction():

    def __init__(self, product_l3_src: ProductL3Src):
        self.product_l3_src = product_l3_src
        self.src_dist_name = SrcDistName(product_l3_src)

    def run_step_function(self):
        json_instruction = json.dumps(
            {'s3_src_tif': self.src_dist_name.s3_src_tif,
             's3_dest_tif': self.src_dist_name.s3_dest_tif,
             's3_hillshade_dest_tif': self.src_dist_name.s3_hillshade_dest_tif
             })
        logging.info(json_instruction)
        client = boto3.client('stepfunctions')
        response = client.start_execution(
            stateMachineArn='',
            name='ausseabed-processing-pipeline-l3',
            input=json_instruction
        )
        logging.info(response)
