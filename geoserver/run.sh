#!/bin/bash
curl -X POST \
  https://generator3.swagger.io/api/generate \
  -H 'content-type: application/json' \
  -d '{
  "specURL" : "https://docs.geoserver.org/latest/en/api/1.0.0/layers.yaml",
  "lang" : "python",
  "type" : "CLIENT",
  "codegenVersion" : "V3"
}' -o layers.zip
