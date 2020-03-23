

resource "aws_db_instance" "asbwarehouse" {
  allocated_storage    = 20
  enabled_cloudwatch_logs_exports = ["postgresql","upgrade"] 
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
  vpc_security_group_ids = [var.rds_security_group]
  db_subnet_group_name=var.public_subnet_grp
  skip_final_snapshot = true // XXX So that we can easily destroy the database in terraform while we are developing
}