# check for presence of all config variables
locals {
  region = "${var.region}"
  account_id = "${var.account_id}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
}

provider "aws" {
  region = "${var.region}"
  profile = "${var.profile}"
}

terraform {
  backend "s3" {}
}

##############################################################################
# VPC
##############################################################################



resource "aws_vpc" "vpc" {
  cidr_block            = "${var.vpc_cidr_block}"
  enable_dns_hostnames  = true

  tags = {
    Name            = "${local.domain}-vpc"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_internet_gateway" "i_gw" {
  vpc_id = "${aws_vpc.vpc.id}"

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_vpc_dhcp_options" "dhcp_options" {
  domain_name         = "$${local.domain}.compute.internal"
  domain_name_servers = ["AmazonProvidedDNS"]

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_vpc_dhcp_options_association" "dhcp_options_assc" {
  vpc_id          = "${aws_vpc.vpc.id}"
  dhcp_options_id = "${aws_vpc_dhcp_options.dhcp_options.id}"
}

##############################################################################
# Public Subnets
##############################################################################

resource "aws_route_table" "rt_public" {
  vpc_id = "${aws_vpc.vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.i_gw.id}"
  }

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_subnet" "subnet_public_b" {
  vpc_id                  = "${aws_vpc.vpc.id}"
  cidr_block              = "${var.subnet_public_b_cidr_block}"
  availability_zone       = "${local.region}b"
  map_public_ip_on_launch = true

  tags = {
    Name            = "${local.domain}-subnet-public-b"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_subnet" "subnet_public_c" {
  vpc_id                  = "${aws_vpc.vpc.id}"
  cidr_block              = "${var.subnet_public_c_cidr_block}"
  availability_zone       = "${local.region}c"
  map_public_ip_on_launch = true

  tags = {
    Name            = "${local.domain}-subnet-public-c"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_route_table_association" "rt_assc_public_b" {
  subnet_id      = "${aws_subnet.subnet_public_b.id}"
  route_table_id = "${aws_route_table.rt_public.id}"
}

resource "aws_route_table_association" "rt_assc_public_c" {
  subnet_id      = "${aws_subnet.subnet_public_c.id}"
  route_table_id = "${aws_route_table.rt_public.id}"
}

##############################################################################
# VPC Security Group
##############################################################################

resource "aws_security_group" "sg" {
  name   = "${local.domain}-sg"
  vpc_id = "${aws_vpc.vpc.id}"

  ingress {
    self      = "true"
    from_port = 0
    to_port   = 0
    protocol  = "-1"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name            = "${local.domain}-sg"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}
