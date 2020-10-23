import sys
import os
from requests.auth import HTTPBasicAuth
from gs_rest_api_workspaces.configuration import Configuration

import six
from six.moves import http_client as httplib
import logging

import json


class ConnectionParameters():
    """ 
    Class that houses connection parameters and reads from a datasource 
    such as environmental variables
    """

    def __init__(self):
        self.geoserver_url = ""
        self.geoserver_password = ""

    def get_auth(self):
        return HTTPBasicAuth('admin', self.geoserver_password)

    def load_from_commandline(self):
        """ Load parameters from environment variables GEOSERVER_URL / GEOSERVER_ADMIN_PASSWORD 
        """

        try:
            self.geoserver_url = os.environ['GEOSERVER_URL']
        except KeyError:
            logging.exception(
                "Please set the environment variable GEOSERVER_URL")
            sys.exit(1)

        logging.info("GEOSERVER_URL = " + self.geoserver_url)

        try:
            self.geoserver_password = json.loads(os.environ['GEOSERVER_ADMIN_PASSWORD'])[
                'TF_VAR_geoserver_admin_password']
        except KeyError:
            logging.exception(
                "Please set the environment variable GEOSERVER_ADMIN_PASSWORD")
            sys.exit(1)

        if ('PRODUCT_CATALOGUE_CREDS' in os.environ):
            # using secretsmanager json config
            json_doc = json.loads(os.environ['PRODUCT_CATALOGUE_CREDS'])
            self.auth_host = json_doc["auth_host"]
            self.auth_client_id = json_doc["auth_client_id"]
            self.auth_client_pem_key = json_doc["client_pem_key"].replace(
                "\\n", "\n")
            self.auth_client_pem_thumprint = json_doc["client_pem_thumbprint"]
        else:
            try:
                self.auth_host = os.environ['AUTH_HOST']
            except KeyError:
                logging.exception(
                    "Please set the environment variable AUTH_HOST")
                sys.exit(1)

            try:
                self.auth_client_id = os.environ['AUTH_CLIENT_ID']
            except KeyError:
                logging.exception(
                    "Please set the environment variable AUTH_CLIENT_ID")
                sys.exit(1)

            try:
                self.auth_client_pem_key = os.environ['CLIENT_PEM_KEY'].replace(
                    "\\n", "\n")
            except KeyError:
                logging.exception(
                    "Please set the environment variable CLIENT_PEM_KEY")
                sys.exit(1)

            try:
                self.auth_client_pem_thumprint = os.environ['CLIENT_PEM_THUMBPRINT']
            except KeyError:
                logging.exception(
                    "Please set the environment variable CLIENT_PEM_THUMBPRINT")
                sys.exit(1)

    def create_configuration(self):
        configuration = Configuration()
        configuration.host = self.geoserver_url + "/rest"
        configuration.username = 'admin'
        configuration.password = self.geoserver_password
        configuration.debug = False

        httplib.HTTPConnection.debuglevel = 0
        return configuration
