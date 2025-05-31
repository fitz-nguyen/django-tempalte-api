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

data "aws_sns_topic" "alarms" {
  for_each = var.health_check_urls

  name = "${local.env}-${each.value.name}-alarms"
}

#resource "aws_route53_health_check" "urls" {

#  for_each = var.health_check_urls

#  fqdn              = each.value.fqdn
#  port              = each.value.port
#  type              = each.value.type
#  resource_path     = each.value.resource_path
#  failure_threshold = each.value.failure_threshold
#  request_interval  = each.value.request_interval

#  tags = {
#    Name = each.value.name
#  }
#}

#resource "aws_cloudwatch_metric_alarm" "urls_healthcheck_failed" {

#  for_each = var.health_check_urls

#  alarm_name          = "${var.env}_${each.value.name}_healthcheck_failed"
#  namespace           = "AWS/Route53"
#  metric_name         = "HealthCheckStatus"
#  comparison_operator = "LessThanThreshold"
#  evaluation_periods  = "1"
#  period              = "60"
#  statistic           = "Minimum"
#  threshold           = "1"
#  unit                = "None"
  #dimensions = {
  #  HealthCheckId = "${aws_route53_health_check.urls[each.value.names].id}"
  #}
#  alarm_description   = "Monitoring whether the service endpoint is down or not."
  #alarm_actions       = ["${data.aws_sns_topic.alarms[each.value.names].arn}"]
  #insufficient_data_actions = ["${var.sns_route53_healthcheck}"]
#  treat_missing_data  = "breaching"
#}