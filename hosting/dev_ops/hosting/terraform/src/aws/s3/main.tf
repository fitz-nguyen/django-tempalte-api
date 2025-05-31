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


resource "aws_s3_bucket_server_side_encryption_configuration" "frontend" {
  bucket = aws_s3_bucket.frontend.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}


resource "aws_s3_bucket_ownership_controls" "frontend-acl-ownership" {
  bucket = aws_s3_bucket.frontend.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
  # Add just this depends_on condition
#  depends_on = [aws_s3_bucket_acl.api_media-acl]
}


resource "aws_s3_bucket_public_access_block" "frontend_public" {
  bucket = "${aws_s3_bucket.frontend.id}"

  block_public_acls   = false
  block_public_policy = false
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


resource "aws_s3_bucket_server_side_encryption_configuration" "api_media" {
  bucket = aws_s3_bucket.api_media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "AES256"
    }
  }
}


resource "aws_s3_bucket_ownership_controls" "api_media-acl-ownership" {
  bucket = aws_s3_bucket.api_media.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
  # Add just this depends_on condition
#  depends_on = [aws_s3_bucket_acl.api_media-acl]
}


resource "aws_s3_bucket_public_access_block" "api_media_public" {
  bucket = "${aws_s3_bucket.api_media.id}"

  block_public_acls   = false
  block_public_policy = false
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
