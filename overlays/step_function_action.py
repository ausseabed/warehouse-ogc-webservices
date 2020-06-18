
import logging
from update_database_action import UpdateDatabaseAction

from product_catalogue_py_rest_client.models import ProductL3Dist, ProductL3Src, RelationSummaryDto, Survey

import json
import re
from src_dist_name import SrcDistName
import boto3
import uuid
from botocore.config import Config

config = Config(
    retries=dict(
        max_attempts=10
    )
)


class StepFunctionAction():

    def __init__(self, product_l3_src: ProductL3Src, state_machine_arn, srs_mapping):
        self.product_l3_src = product_l3_src
        self.src_dist_name = SrcDistName(product_l3_src)
        self.state_machine_arn = state_machine_arn
        self.srs_mapping = srs_mapping

    def run_step_function(self):
        srs_matches = [match for match in self.srs_mapping if 'EPSG:' +
                       str(match['Code']) == self.product_l3_src.srs]

        if (len(srs_matches) == 0):
            multiplier = 1
            logging.info('No srs found for ' + self.product_l3_src.name)
        else:
            srs_match = srs_matches[0]
            srs_type = srs_match['Type']
            logging.info('SRS '+srs_type+' found for ' +
                         self.product_l3_src.name)
            if (srs_type.startswith('geog')):
                logging.info('Geographic type')
                multiplier = 111120
            else:
                logging.info('Projected type')
                multiplier = 1

        json_instruction = json.dumps(
            {'s3_src_tif': self.src_dist_name.s3_src_tif,
             's3_dest_tif': self.src_dist_name.s3_dest_tif,
             's3_hillshade_dest_tif': self.src_dist_name.s3_hillshade_dest_tif,
             's3_scaling_factor': str(multiplier)
             })
        logging.info(json_instruction)
        client = boto3.client('stepfunctions', config=config)
        product_build = re.sub("[^a-zA-Z0-9]", "_",
                               self.product_l3_src.name)[0:39] + "_" + str(uuid.uuid4())
        response = client.start_execution(
            stateMachineArn=self.state_machine_arn,
            name=product_build,
            input=json_instruction
        )
        logging.info(response)
