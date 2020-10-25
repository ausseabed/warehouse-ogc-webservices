import json
import os
print(json.loads(os.environ['GEOSERVER_ADMIN_PASSWORD'])[
      'TF_VAR_geoserver_admin_password'])
