import time
import logging
import gs_rest_api_owsservices
from gs_rest_api_owsservices.rest import ApiException
from gs_rest_api_owsservices import WMSInfoWrapper, WMSInfo, WCSInfo, WCSInfoWrapper


class ServiceDescriptionAddTask(object):
    def __init__(self, configuration, workspace_name):
        self.configuration = configuration
        self.workspace_name = workspace_name

    def run_wms(self):
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_owsservices.DefaultApi(
            gs_rest_api_owsservices.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get wms for workspace
            api_response = api_instance.get_wms_settings()
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_wms_settings: %s\n" % e)

        logging.info(api_response)
        wms_config = api_response.wms
        wms_config.enabled = True
        wms_config.name = "WMS"
        wms_config.title = "Ausseabed Warehouse Bathymetry"
        wms_config.maintainer = "http://www.ausseabed.gov.au"
        # Spelling mistake part of geoserver's rest interface
        wms_config.abstrct = "This web service contains marine geospatial bathymetry held by Geoscience Australia and the Ausseabed community. It includes bathymetry plus derived layers. This web service allows exploration of the seafloor topography through the compilation of multibeam sonar and other marine datasets."
        wms_config.access_constraints = "Unless otherwise stated, © Commonwealth of Australia (Geoscience Australia) 2020. This product is released under the Creative Commons Attribution 4.0 International Licence. http://creativecommons.org/licenses/by/4.0/legalcode"
        wms_config_wrapper = WMSInfoWrapper(wms_config)

        logging.info("Writing WMS abstract for {}".format(self.workspace_name))

        try:
            api_response = api_instance.put_wms_settings(wms_config_wrapper)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->put_wms_settings: %s\n" % e)

        try:
            api_response = api_instance.put_wms_workspace_settings(
                wms_config_wrapper, self.workspace_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->put_wms_workspace_settings: %s\n" % e)

    def run_wcs(self):
        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_owsservices.DefaultApi(
            gs_rest_api_owsservices.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        try:
            # Get wms for workspace
            api_response = api_instance.get_wcs_settings()
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->get_wcs_settings: %s\n" % e)

        logging.info(api_response)
        wcs_config: WCSInfo = api_response.wcs
        wcs_config.enabled = "True"
        wcs_config.name = "WCS"
        wcs_config.title = "Ausseabed Warehouse Bathymetry"
        wcs_config.maintainer = "http://www.ausseabed.gov.au"
        # Spelling mistake part of geoserver's rest interface
        wcs_config.abstrct = "This web service contains marine geospatial bathymetry held by Geoscience Australia and the Ausseabed community. It includes bathymetry plus derived layers. This web service allows exploration of the seafloor topography through the compilation of multibeam sonar and other marine datasets."
        wcs_config.access_constraints = "Unless otherwise stated, © Commonwealth of Australia (Geoscience Australia) 2020. This product is released under the Creative Commons Attribution 4.0 International Licence. http://creativecommons.org/licenses/by/4.0/legalcode"
        wcs_config.max_input_memory = 0
        wcs_config.max_output_memory = 0
        wcs_config_wrapper = WCSInfoWrapper(wcs_config)

        logging.info("Writing WCS abstract for {}".format(self.workspace_name))

        try:
            api_response = api_instance.put_wcs_settings(wcs_config_wrapper)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->put_wcs_settings: %s\n" % e)
        try:
            api_response = api_instance.put_wcs_workspace_settings(
                wcs_config_wrapper, self.workspace_name)
        except ApiException as e:
            logging.error(
                "Exception when calling DefaultApi->put_wcs_workspace_settings: %s\n" % e)

    def run(self):
        logging.info("Creating service description {}".format(
            self.workspace_name))
        self.run_wms()
        self.run_wcs()
