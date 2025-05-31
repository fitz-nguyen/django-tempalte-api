variable "region" {
  description = "The AWS region to create things in."
  default     = "us-east-1"
}

variable "account_id" {
  description = "The AWS Account ID"
}

variable "env" {
  description = "Your Environment"
}

variable "domain" {
  description = "Your Domain"
}

variable "profile" {
  description = "AWS Profile"
}

variable "tag_version" {
  description = "Version of terraform"
  default = "1.0"
}

variable "tag_strategy" {
  description = "Strategy"
  default = "Terraform"
}

variable "frontend_aliases" {
  description = "Cloudfront Aliases"
}

variable "frontend_cert_arn" {
  description = "SSL Cert Arn"
}

variable "ssh_key_name" {
  description = "Name of the ssh pair key"
}

variable "ubuntu_ami" {
  description = "AMI to use"
  default = "ami-064a0193585662d74"
}