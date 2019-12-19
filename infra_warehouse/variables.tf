variable "aws_region" {}

#------ storage variables



#-------networking variables

variable "vpc_cidr" {}

variable "public_cidrs" {
  type = "list"
}

variable "accessip" {}

#-------compute variables

#variable "fargate_cpu"{}
#variable "fargate_memory"{}
variable "geoserver_image"{} # based on kartoza/geoserver
variable "geoserverpush_image"{} # to push new data onto the geoserver instance

variable "server_cpu"{}
variable "server_memory"{}

variable "geoserver_initial_memory"{}
variable "geoserver_maximum_memory"{}
variable "geoserver_admin_password"{}