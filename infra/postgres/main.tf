

resource "aws_db_instance" "default" {
  allocated_storage    = 20
  //availability_zone = var.aws_region
  //enabled_cloudwatch_logs_exports = true
  iam_database_authentication_enabled = false
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "11.6"
  instance_class       = var.postgres_server_spec 
  name                 = "asbwarehouse"
  username             = "postgres"
  password             = var.postgres_admin_password
  //parameter_group_name = "default.mysql5.7"
  port = 5432 
  //db_subnet_group_name = var.rds_subnet_group
  //vpc_security_group_ids = var.public_sg
}