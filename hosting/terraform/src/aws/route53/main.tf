locals {
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

data "aws_vpc" "vpc" {
  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

resource "aws_route53_health_check" "urls" {

  for_each = var.health_check_urls

  fqdn              = each.value.fqdn
  port              = each.value.port
  type              = each.value.type
  resource_path     = each.value.resource_path
  failure_threshold = each.value.failure_threshold
  request_interval  = each.value.request_interval

  tags = {
    Name = each.value.name
  }
}