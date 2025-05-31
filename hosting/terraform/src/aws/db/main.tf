# check for presence of all config variables
locals {
  account_id  = "${var.account_id}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  db_name     = "${var.db_name}"
  db_password = "${var.db_password}"
  db_username = "${var.db_username}"
  //db_password_test = "${var.db_password_test}"
  //db_username_test = "${var.db_username_test}"
}

data "aws_vpc" "vpc" {
  tags = {
    Name            = "${local.domain}-vpc"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

data "aws_security_group" "sg" {
  name = "${local.domain}-sg"

  tags = {
    Name            = "${local.domain}-sg"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

provider "aws" {
  region = "${var.region}"
  profile = "${var.profile}"
}

terraform {
  backend "s3" {}
}

data "aws_subnet_ids" "subnet_ids" {
  vpc_id = "${data.aws_vpc.vpc.id}"
}

resource "aws_db_subnet_group" "subnet_group" {
  name       = "${local.domain}"
  subnet_ids = "${data.aws_subnet_ids.subnet_ids.ids}"

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

data "aws_security_group" "public_access" {
  name = "${local.domain}-public_db_access"
}

data "aws_kms_alias" "vpc-variables" {
  name          = "alias/${local.domain}-vpc-variables"
}

/*
resource "aws_rds_cluster" "main_cluster" {
  count                  = "${local.production ? 1 : 0}"
  cluster_identifier     = "main-cluster"
  database_name          = "${local.db_name}"
  kms_key_id             = "${aws_kms_key.db.arn}"
  master_password        = "${local.db_password}"
  master_username        = "${local.db_username}"
  engine                 = "mariadb"
  engine_version         = "10.2"
  availability_zones     = ["${local.region}a", "${local.region}b", "${local.region}c"]
  db_subnet_group_name   = "${aws_db_subnet_group.subnet_group.name}"
  vpc_security_group_ids = ["${local.production ? "${data.aws_security_group.sg.id}" : "${aws_security_group.public_access.id}"}"]

  storage_encrypted                   = "${local.production}"
  iam_database_authentication_enabled = false

  skip_final_snapshot = "${!local.production}"
}

resource "aws_rds_cluster_instance" "cluster_instances" {
  count               = "${local.production ? 2 : 0}"
  identifier          = "main-cluster-instance-${count.index}"
  cluster_identifier  = "${aws_rds_cluster.main_cluster.id}"
  engine              = "aurora-postgresql"
  engine_version      = "9.6.3"
  instance_class      = "db.r4.large"
  publicly_accessible = "${!local.production}"
  apply_immediately   = "${!local.production}"
}
*/

resource "aws_db_instance" "db" {
  allocated_storage      = 40
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "10.6"
  instance_class         = "${var.db_instance_size}"
  identifier             = "${local.env}${local.db_name}"
  name                   = "${local.env}${local.db_name}"
  username               = "${local.db_username}"
  password               = "${local.db_password}"
  publicly_accessible    = "${var.db_publically_accessible}"
  skip_final_snapshot    = false

  db_subnet_group_name   = "${aws_db_subnet_group.subnet_group.name}"

  // kms_key_id             = "${data.aws_kms_key.db.arn}"
  //storage_encrypted                   = "${local.env == "production" ? true : false}"
  iam_database_authentication_enabled = false

  vpc_security_group_ids = ["${data.aws_security_group.sg.id}","${data.aws_security_group.public_access.id}"]

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

/*
resource "aws_db_instance" "test" {
  db_subnet_group_name   = "${aws_db_subnet_group.subnet_group.name}"
  vpc_security_group_ids = ["${aws_security_group.public_access.id}"]
  count                  = "${!local.production ? 1 : 0}"
  allocated_storage      = 40
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "9.6.3"
  instance_class         = "db.t2.small"
  name                   = "${local.db_name_test}"
  username               = "${local.db_username_test}"
  password               = "${local.db_password_test}"
  publicly_accessible    = "${!local.production}"
  skip_final_snapshot    = "${!local.production}"
}
*/



