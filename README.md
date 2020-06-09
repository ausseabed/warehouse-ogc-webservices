
[![CircleCI](https://circleci.com/gh/ausseabed/warehouse-ogc-webservices.svg?style=svg)](https://circleci.com/gh/ausseabed/warehouse-ogc-webservices)


AusSeabed is a national seabed mapping coordination program. The program aims to serve the Australian community that relies on seabed data by coordinating collection efforts in Australian waters and improving data access. 

This repository contains the code that builds OGC web service endpoints. Geoserver on AWS ECS Fargate infrastructure is used to provide the endpoints. The terraform code for deploying the infrastructure is housed in the https://github.com/ausseabed/ausseabed-aws-foundation/ repository.

 
______________________________________________________________________________________________________________

#### Build Workflow
Circle CI builds and pushes the docker container. The steps involved in the build are:
* build_tomcat_push_jar (create a launch script to pull configuration data)
* build_and_push_geoserver_image (incorporate the launch script and any other configuration details into a docker container)


______________________________________________________________________________________________________________

#### Build Tomcat Push Jar
A very simple jar file is added to the TomCat service to allow push-on-load configuration of the GeoServer Instance. This is located in warehouse-ogc-webservices/geoserver/ausseabed.pipeline/

______________________________________________________________________________________________________________

#### Push on load
On load of the geoserver instance, the entrypoint warehouse-ogc-webservices/geoserver/geoserverpush/push_geoserver_settings.py runs to transfer information about layers from the Product Catalogue to the geoserver instance. The Product Catalogue restful interface is defined in the repo: https://github.com/ausseabed/product-catalogue. Geoserver is called through a set of restful libraries defined in the repo: https://github.com/ausseabed/geoserver-rest-client. These commands can be run to populate
