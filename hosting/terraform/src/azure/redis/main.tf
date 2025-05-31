# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  location = "${var.location}"
}

provider "azurerm" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

##############################################################################
# REDIS
##############################################################################

data "azurerm_resource_group" "project" {
  name     = "${local.domain}-resources"
}

# NOTE: the Name used for Redis needs to be globally unique
resource "azurerm_redis_cache" "example" {
  name                = "${local.domain}-redis-cache"
  location            = "${data.azurerm_resource_group.project.location}"
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  capacity            = 2
  family              = "C"
  sku_name            = "Standard"
  enable_non_ssl_port = true
  minimum_tls_version = "1.2"

  redis_configuration {}
}

output "redis_hostname" {
  value = "${azurerm_redis_cache.example.hostname}"
}
output "redis_primary_access_key" {
  value = "${azurerm_redis_cache.example.primary_access_key}"
}
output "redis_port" {
  value = "${azurerm_redis_cache.example.port}"
}