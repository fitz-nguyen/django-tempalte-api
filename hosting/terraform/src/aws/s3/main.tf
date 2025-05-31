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

resource "aws_s3_bucket" "frontend" {

  bucket = "${var.frontend_aliases}"
  acl    = "public-read"
  force_destroy = true

  website {
    index_document = "index.html"
    error_document = "error.html"
  }

  versioning {
    enabled = true
  }

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}
resource "aws_s3_bucket_policy" "frontend" {

  bucket = "${aws_s3_bucket.frontend.id}"

  policy = <<POLICY
{
  "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "${aws_s3_bucket.frontend.arn}/*"
            ]
        }
    ]
}
POLICY
}

resource "aws_s3_bucket" "api_media" {

  bucket = "${local.domain}-api-media"
  acl    = "public-read"
  force_destroy = true

  versioning {
    enabled = true
  }

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}
resource "aws_s3_bucket_policy" "api_media" {

  bucket = "${aws_s3_bucket.api_media.id}"

  policy = <<POLICY
{
  "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "${aws_s3_bucket.api_media.arn}/*"
            ]
        }
    ]
}
POLICY
}
