import gs_rest_api_styles
from gs_rest_api_styles.rest import ApiException

import os
import sys
import logging


class StyleAddTask(object):

    LOCAL_STYLE_FILENAME = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/bathymetry_transparent.sld"
    BATH_ALT_LOCAL_STYLE_FILENAME = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/bathymetry_shallow.sld"
    BATH_HILLSHADE_STYLE_FILENAME = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/bathymetry_hillshade.sld"

    AUSSEABED_BATHY_HOLDINGS_PURPLE = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/ausseabed_bathy_holdings_purple.sld"
    AUSSEABED_BATHY_HOLDINGS_BY_SOURCE = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/Ausseabed_bathy_by_source.sld"
    AUSSEABED_BATHY_WITH_DATA_ACCESS = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/Ausseabed_with_data_access.sld"

    MH370_PHASE2 = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/phase2_data.sld"
    MH370_PHASE2_INVERSE = os.path.dirname(os.path.realpath(__file__)) + \
        "/styles/phase2_data_inverse.sld"

    BATH_STYLE_NAME = "Bathymetry"
    BATH_ALT_STYLE_NAME = "BathymetryShallow"
    BATH_HILLSHADE_STYLE_NAME = "BathymetryHillshade"
    AUSSEABED_BATHY_HOLDINGS_PURPLE_NAME = "HoldingsPurple"
    AUSSEABED_BATHY_HOLDINGS_BY_SOURCE_NAME = "HoldingsBySource"
    AUSSEABED_BATHY_WITH_DATA_ACCESS_NAME = "HoldingsDataAccess"
    MH370_PHASE2_STYLE_NAME = "MH370Phase2"
    MH370_PHASE2_INVERSE_STYLE_NAME = "MH370Phase2Inverse"

    POLY_STYLE_NAME = "polygon"

    def __init__(self, configuration, workspace_name):
        self.configuration = configuration
        self.workspace_name = workspace_name

        self.styles = {
            self.BATH_STYLE_NAME: self.LOCAL_STYLE_FILENAME,
            self.BATH_ALT_STYLE_NAME: self.BATH_ALT_LOCAL_STYLE_FILENAME,
            self.BATH_HILLSHADE_STYLE_NAME: self.BATH_HILLSHADE_STYLE_FILENAME,
            self.AUSSEABED_BATHY_HOLDINGS_PURPLE_NAME: self.AUSSEABED_BATHY_HOLDINGS_PURPLE,
            self.AUSSEABED_BATHY_HOLDINGS_BY_SOURCE_NAME: self.AUSSEABED_BATHY_HOLDINGS_BY_SOURCE,
            self.AUSSEABED_BATHY_WITH_DATA_ACCESS_NAME: self.AUSSEABED_BATHY_WITH_DATA_ACCESS,
            self.MH370_PHASE2_STYLE_NAME: self.MH370_PHASE2,
            self.MH370_PHASE2_INVERSE_STYLE_NAME: self.MH370_PHASE2_INVERSE
        }

    def create_style(self, style_name, local_file_name):
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_client = gs_rest_api_styles.ApiClient(
            self.configuration, header_name='Authorization', header_value=authtoken)

        # str | Content-Type of the style file. Used to determine style encoding when POSTing a style file (e.g. SLD or SE). (optional)
        content_type = 'application/vnd.ogc.sld+xml'

        # The content-type gets overriden by swagger in the client...
        # However, the swagger client content-type gets overriden by the default header...
        api_client.set_default_header('Content-Type', content_type)
        api_instance = gs_rest_api_styles.DefaultApi(api_client)

        logging.info("Creating style {}".format(style_name))

        local_file_handle = open(local_file_name, mode='r')
        body = local_file_handle.read()
        local_file_handle.close()
        try:
            # Add a new style to a given workspace
            api_instance.post_workspace_styles(
                body, self.workspace_name, content_type=content_type, name=style_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->post_workspace_styles: %s\n" % e)

    def get_styles(self):
        # create an instance of the API class
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_styles.DefaultApi(
            gs_rest_api_styles.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        workspace = self.workspace_name

        try:
            # Get a list of styles in a given workspace
            api_response = api_instance.get_workspace_styles(workspace)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_workspace_styles: %s\n" % e)

        if api_response['styles'] == '':
            style_names = []
        else:
            style_names = [style_record['name']
                           for style_record in api_response['styles']['style']]
        return style_names

    def run(self):

        existing_styles = self.get_styles()
        logging.info("Found existing styles {}".format(existing_styles))

        for (style_name, local_file_name) in self.styles.items():
            if not(style_name in existing_styles):
                self.create_style(style_name, local_file_name)
