
import logging
from update_database_action import UpdateDatabaseAction

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey

import json
import re
from src_dist_name import SrcDistName
import boto3
import uuid


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
        product_build = re.sub("[^a-zA-Z0-9]", "_",
                               self.product_l3_src.name) + "_" + str(uuid.uuid4())
        response = client.start_execution(
            stateMachineArn='',
            name=product_build,
            input=json_instruction
        )
        logging.info(response)
