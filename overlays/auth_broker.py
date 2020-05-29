import sys
import json

import requests
import msal

import logging
import urllib


class AuthBroker():
    """ 
    Class that houses connection parameters and reads from a datasource 
    such as environmental variables
    """

    def __init__(self, connection_parameters):
        self.connection_parameters = connection_parameters

    def get_auth_token(self):
        self.authority = self.connection_parameters.auth_host
        self.client_id = self.connection_parameters.auth_client_id
        self.client_credential = {"thumbprint": self.connection_parameters.auth_client_pem_thumprint,
                                  "private_key": self.connection_parameters.auth_client_pem_key}

        app = msal.ConfidentialClientApplication(
            self.client_id, authority=self.authority,
            client_credential=self.client_credential
        )

        # The pattern to acquire a token looks like this.
        result = None

        # Firstly, looks up a token from cache
        # Since we are looking for token for the current app, NOT for an end user,
        # notice we give account parameter as None.
        result = app.acquire_token_silent(
            [self.client_id + "/.default"], account=None)

        if not result:
            logging.info(
                "No suitable token exists in cache. Let's get a new one from AAD.")
            result = app.acquire_token_for_client(
                scopes=[self.client_id + "/.default"])

        if not("access_token" in result):
            logging.error("Could not find access token")
            sys.exit(1)
        else:
            return result["access_token"]
