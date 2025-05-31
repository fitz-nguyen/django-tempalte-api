provider "aws" {
  region = "${var.region}"
}

terraform {
  backend "s3" {}
}

locals {
  region = "${var.region}"
  account_id = "${var.account_id}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
}

resource "aws_sns_topic" "alarms" {

  for_each = var.health_check_urls

  name = "${local.env}-${each.value.name}-alarms"

  provisioner "local-exec" {
    command = "aws sns subscribe --topic-arn ${self.arn} --region ${local.region} --protocol email --notification-endpoint ${each.value.notification_email}"
  }

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}