# check for presence of all config variables
locals {
  account_id  = "${var.account_id}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  db_name     = "${var.db_name}"
  db_password = "${var.db_password}"
  db_username = "${var.db_username}"
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

data "aws_subnets" "subnet_ids" {
  filter {
    name   = "vpc-id"
    values = ["${data.aws_vpc.vpc.id}"]
  }
}

resource "aws_db_subnet_group" "subnet_group" {
  name       = "${local.domain}"
  subnet_ids = "${data.aws_subnets.subnet_ids.ids}"

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_security_group" "public_access" {
  name        = "${local.domain}-public-db-access-sg"
  description = "${local.domain} publicly accessible"
  vpc_id      = "${data.aws_vpc.vpc.id}"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = ["${data.aws_security_group.sg.id}"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = -1
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name            = "${local.domain}-public-db-access-sg"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_db_instance" "db" {
  allocated_storage      = 40
  storage_type           = "gp2"
  engine                 = "postgres"
  engine_version         = "14.17"
  instance_class         = "${var.db_instance_size}"
  identifier             = "${local.env}-${local.db_name}"
  db_name                = "${local.env}_${local.db_name}"
  username               = "${local.db_username}"
  password               = "${local.db_password}"
  publicly_accessible    = "${var.db_publically_accessible}"
  skip_final_snapshot    = false
  backup_retention_period= 7

  db_subnet_group_name   = "${aws_db_subnet_group.subnet_group.name}"

  storage_encrypted                   = true
  iam_database_authentication_enabled = false

  vpc_security_group_ids = ["${data.aws_security_group.sg.id}","${aws_security_group.public_access.id}"]

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}