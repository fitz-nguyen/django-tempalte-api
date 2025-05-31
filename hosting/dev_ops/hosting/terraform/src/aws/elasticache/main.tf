locals {
  region = "${var.region}"
  account_id = "${var.account_id}"
  ssh_key_name = "${var.ssh_key_name}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  ubuntu_ami   = "${var.ubuntu_ami}"
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

data "aws_subnet" "subnet_public_b" {
  tags = {
    Name            = "${local.domain}-subnet-public-b"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

data "aws_subnet" "subnet_public_c" {
  tags = {
    Name            = "${local.domain}-subnet-public-c"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
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

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${local.domain}-cache-subnet"
  subnet_ids = ["${data.aws_subnet.subnet_public_b.id}","${data.aws_subnet.subnet_public_c.id}"]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${local.domain}-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis7"
  port                 = 6379

  subnet_group_name = "${aws_elasticache_subnet_group.redis.name}"
  security_group_ids = ["${data.aws_security_group.sg.id}"]

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

output "cache_nodes" {
  value = "${aws_elasticache_cluster.redis.cache_nodes}"
}