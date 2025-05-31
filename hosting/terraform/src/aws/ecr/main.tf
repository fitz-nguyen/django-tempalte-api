locals {
  account_id = "${var.account_id}"
  ssh_key_name = "${var.ssh_key_name}"
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

data "aws_vpc" "vpc" {
  tags = {
    Name            = "${local.domain}-vpc"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_ecr_repository" "app" {
  name = "${local.domain}"

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

output "aws_ecr_repository" {
  value = "${aws_ecr_repository.app.repository_url}"
}