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

variable "ssh_key_name" {
  description = "Name of the ssh pair key"
}

variable "db_username" {
  description = "Username for the db"
}

variable "db_password" {
  description = "Password for the db"
}

variable "db_name" {
  description = "Name of the db"
}