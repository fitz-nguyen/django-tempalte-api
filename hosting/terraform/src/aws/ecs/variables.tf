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

variable "ssh_key_name" {
  description = "Name of the ssh pair key"
}

variable "ubuntu_ami" {
  description = "AMI to use"
  default = "ami-064a0193585662d74"
}

variable "az_count" {
  description = "Number of AZs to cover in a given AWS region"
  default     = "2"
}

variable "api_proxy_port" {
  description = "Api Proxy port exposed by the docker image to redirect traffic to"
  default     = 8000
}

variable "api_count" {
  description = "Number of API docker containers to run"
  default     = 1
}

variable "fargate_api_docker_image_uri" {
  description = "Docker image uri for app"
}

variable "pgbouncer_port" {
  description = "PGBouncer port exposed by the docker image to redirect traffic to"
  default     = 6432
}

variable "pgbouncer_count" {
  description = "Number of pgbouncer docker containers to run"
  default     = 1
}

variable "fargate_pgbouncer_docker_image_uri" {
  description = "Docker image uri for pgbouncer"
}

variable "web_proxy_port" {
  description = "Web Proxy port exposed by the docker image to redirect traffic to"
  default     = 80
}

variable "web_proxy_count" {
  description = "Number of web proxy docker containers to run"
  default     = 1
}

variable "fargate_web_proxy_docker_image_uri" {
  description = "Docker image uri for web proxy"
  default     = "nginx-1.17.10-alpine"
}

variable "redis_port" {
  description = "Redis port"
  default = 6379
}

variable "redis_count" {
  description = "Number of redis docker containers to run"
  default     = 1
}

variable "fargate_redis_docker_image_uri" {
  description = "Docker image uri for redis"
  default     = "redis:6.0-rc4-alpine"
}

variable "fargate_cpu" {
  description = "Fargate instance CPU units to provision (1 vCPU = 1024 CPU units)"
  default     = 512
}

variable "fargate_memory" {
  description = "Fargate instance memory to provision (in MiB)"
  default     = 512
}

variable "db_name" {
  description = "Name of the db"
}

variable "db_username" {
  description = "Username for the db"
}

variable "db_password" {
  description = "Password for the db"
}

variable "tag_version" {
  description = "Version of terraform"
  default = "1.0"
}

variable "tag_strategy" {
  description = "Strategy"
  default = "Terraform"
}

variable "deployment_maximum_percent" {
  default     = 200
  type        = string
  description = "The upper limit (as a percentage of the service's desiredCount) of the number of running tasks that can be running in a service during a deployment."
}

variable "deployment_minimum_healthy_percent" {
  default     = 100
  type        = string
  description = "The lower limit (as a percentage of the service's desiredCount) of the number of running tasks that must remain running and healthy in a service during a deployment."
}

variable "deployment_controller_type" {
  default     = "ECS"
  type        = string
  description = "Type of deployment controller. Valid values: CODE_DEPLOY, ECS."
}

variable "health_check_grace_period_seconds" {
  default     = 60
  type        = string
  description = "Seconds to ignore failing load balancer health checks on newly instantiated tasks to prevent premature shutdown, up to 7200."
}

variable "platform_version" {
  default     = "1.4.0"
  type        = string
  description = "The platform version on which to run your service."
}