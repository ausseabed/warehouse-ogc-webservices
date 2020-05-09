import time
import gs_rest_api_workspaces
from gs_rest_api_workspaces.rest import ApiException

from gs_rest_api_workspaces.model import Workspace
from pprint import pprint
import logging


class WorkspaceAddTask(object):
    def __init__(self, configuration, workspace_name):
        self.configuration = configuration
        self.workspace_name = workspace_name

    def run(self):
        logging.info("Creating workspace {}".format(self.workspace_name))

        authtoken = self.configuration.get_basic_auth_token()
        # create an instance of the API class
        api_instance = gs_rest_api_workspaces.DefaultApi(
            gs_rest_api_workspaces.ApiClient(self.configuration, header_name='Authorization', header_value=authtoken))

        authtoken = self.configuration.get_basic_auth_token()
        try:
            # Get a list of workspaces
            api_response = api_instance.get_workspaces()
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling DefaultApi->get_workspaces: %s\n" % e)

        workspace_names = [workspace['name']
                           for workspace in api_response.workspaces['workspace']]

        logging.info("Found workspaces {}".format(workspace_names))

        if not(self.workspace_name in workspace_names):
            # create an instance of the API class
            # Workspace | The layer group body information to upload.
            body = gs_rest_api_workspaces.model.Workspace(
                {'name': self.workspace_name})
            # bool | New workspace will be the used as the default. Allowed values are true or false,  The default value is false. (optional)
            default = False

            try:
                # add a new workspace to GeoServer
                api_response = api_instance.post_workspaces(
                    body, default=default)
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling DefaultApi->post_workspaces: %s\n" % e)
