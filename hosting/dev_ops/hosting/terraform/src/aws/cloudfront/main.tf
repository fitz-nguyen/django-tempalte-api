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

provider "aws" {
  alias  = "east-1"
  region = "us-east-1"
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

data "aws_s3_bucket" "frontend" {
  bucket = "${var.frontend_aliases}"
}

module "security_header_lambda" {
  source                 = "transcend-io/lambda-at-edge/aws"
  version                = "0.0.2"
  name                   = "security_headers_${var.env}"
  description            = "Adds security headers to the request"
  runtime                = "nodejs14.x"
  lambda_code_source_dir = "${path.module}/functions"

  providers              = {
    aws                  = aws.east-1
  }
}


resource "aws_cloudfront_distribution" "s3_distribution" {
    origin {
        domain_name = "${data.aws_s3_bucket.frontend.bucket_regional_domain_name}"
        origin_id   = "S3-${data.aws_s3_bucket.frontend.bucket}"
    }

    default_root_object = "index.html"
    enabled = true

    default_cache_behavior {
        allowed_methods = ["GET", "HEAD"]
        cached_methods = ["GET", "HEAD"]
        target_origin_id = "S3-${data.aws_s3_bucket.frontend.bucket}"

        # Forward all query strings, cookies and headers
        forwarded_values {
            query_string = false
            cookies {
                forward = "none"
            }
        }
        lambda_function_association {
          event_type   = "origin-request"
          lambda_arn   = module.security_header_lambda.arn
          include_body = false
        }


        viewer_protocol_policy = "redirect-to-https"
        min_ttl = 0
        default_ttl = 30
        max_ttl = 86400
    }

    # Distributes content to US and Europe
    price_class = "PriceClass_100"

    aliases = ["${var.frontend_aliases}"]

    # Restricts who is able to access this content
    restrictions {
        geo_restriction {
            # type of restriction, blacklist, whitelist or none
            restriction_type = "none"
        }
    }


    # SSL certificate for the service.
    viewer_certificate {
        acm_certificate_arn      = "${var.frontend_cert_arn}"
        ssl_support_method       = "sni-only"
        minimum_protocol_version = "TLSv1"
        // cloudfront_default_certificate = true
    }


    custom_error_response {
      error_caching_min_ttl = "0"
      error_code = 404
      response_code = 200
      response_page_path = "/index.html"
    }
    custom_error_response {
      error_caching_min_ttl = "0"
      error_code = 403
      response_code = 200
      response_page_path = "/index.html"
    }

    tags = {
      Domain          = "${var.domain}"
      Environment     = "${var.env}"
      Version         = "${var.tag_version}"
      Strategy        = "${var.tag_strategy}"
    }
}