#!/bin/bash
# FARGATE secrets are exported as JSON: {"TF_VAR_geoserver_admin_password":"..."}
# Convert to normal exports and run script
# e.g. /usr/local/pulldata/decode_aws_json.sh /scripts/entrypoint.sh
export GEOSERVER_ADMIN_PASSWORD=`python3 /usr/local/pulldata/decode_json.py`
$@
