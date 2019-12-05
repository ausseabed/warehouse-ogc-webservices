provider "aws" {
  region = "${var.aws_region}"
}

terraform {
  backend "s3" {
    bucket = "ausseabed-processing-pipeline-tf-infra"
    key    = "terraform/terraform-server.tfstate"
    region = "ap-southeast-2"
  }
}


module "networking" {
  source       = "./networking"
  vpc_cidr     = "${var.vpc_cidr}"
  public_cidrs = "${var.public_cidrs}"
  accessip     = "${var.accessip}"
}


module "ancillary" {
  source = "./ancillary"
}

module "geoserver" {
  source       = "./geoserver"
  server_cpu                 = "${var.server_cpu}"
  server_memory              = "${var.server_memory}"  
  ecs_task_execution_role_svc_arn = "${module.ancillary.ecs_task_execution_role_svc_arn}"
  public_subnets  = "${module.networking.public_subnets}"
  public_sg = "${module.networking.public_sg}"
}

module "mapserver" {
  source       = "./mapserver"
  server_cpu                 = "${var.server_cpu}"
  server_memory              = "${var.server_memory}"
  ecs_task_execution_role_svc_arn = "${module.ancillary.ecs_task_execution_role_svc_arn}"
  public_subnets  = "${module.networking.public_subnets}"
  public_sg = "${module.networking.public_sg}"
}
