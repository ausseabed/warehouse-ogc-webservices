#!/bin/bash
# FARGATE secrets are exported as JSON: {"TF_VAR_geoserver_admin_password":"..."}
# Convert to normal exports
export GEOSERVER_ADMIN_PASSWORD=`python3 /usr/local/pulldata/decode_json.py`
$@
