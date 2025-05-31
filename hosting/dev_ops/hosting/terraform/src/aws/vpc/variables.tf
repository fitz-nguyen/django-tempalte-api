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

variable "vpc_cidr_block" {
  description = "cidr block"
  default = "10.0.0.0/16"
}

variable "subnet_public_b_cidr_block" {
  description = "Public B cidr block"
}

variable "subnet_public_c_cidr_block" {
  description = "Public C cidr block"
}