import sys
import os
from requests.auth import HTTPBasicAuth

import six
from six.moves import http_client as httplib
import logging


class ConnectionParameters():
    """ 
    Class that houses connection parameters and reads from a datasource 
    such as environmental variables
    """

    def load_from_commandline(self):
        """ Load parameters from environment variables GEOSERVER_URL / GEOSERVER_ADMIN_PASSWORD 
        """

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
            self.auth_client_pem_key = os.environ['CLIENT_PEM_KEY']
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
