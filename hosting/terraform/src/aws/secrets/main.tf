locals {
  account_id = "${var.account_id}"
  ssh_key_name = "${var.ssh_key_name}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  db_name     = "${var.db_name}"

  env_secret = {
    ENVIRONMENT = "${local.env}"
    BASE_URL = "http://localhost"
    FRONTEND_BASE_URL = "http://localhost"
    DATABASE_URL = "postgres://${var.db_username}:${var.db_password}@${data.aws_db_instance.db.address}:5432/${var.db_name}"
  }
}

provider "aws" {
  region = "${var.region}"
  profile = "${var.profile}"
}

terraform {
  backend "s3" {}
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

data "aws_db_instance" "db" {
  db_instance_identifier = "${local.env}${local.db_name}"
}

data "aws_kms_alias" "vpc_variables" {
  name = "alias/${local.domain}-vpc-variables"
}

resource "aws_secretsmanager_secret" "secrets" {
  name = "${local.domain}-vpc-secrets"
  kms_key_id = "${data.aws_kms_alias.vpc_variables.target_key_id}"
}
resource "aws_secretsmanager_secret_version" "config" {
  secret_id     = "${aws_secretsmanager_secret.secrets.id}"
  secret_string = "${jsonencode(local.env_secret)}"
}