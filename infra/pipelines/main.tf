locals {
  pipeline_vars = { 
    "ausseabed_sm_role" = var.ausseabed_sm_role
    "aws_ecs_cluster_arn" = var.aws_ecs_cluster_arn
    "aws_ecs_task_definition_gdal_arn" = var.aws_ecs_task_definition_gdal_arn
    "aws_ecs_task_definition_caris_sg" = var.aws_ecs_task_definition_caris_sg
    "aws_ecs_task_definition_caris_subnet" = var.aws_ecs_task_definition_caris_subnet
  }
}

resource "aws_sfn_state_machine" "ausseabed-processing-pipeline-l3" {
  name     = "ausseabed-processing-pipeline-l3"
  role_arn = "${var.ausseabed_sm_role}"
  
  definition = templatefile("${path.module}/process_L3.json",local.pipeline_vars)
}