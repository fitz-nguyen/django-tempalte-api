# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  bastion_name = "${local.domain}-bastion"
  location = "${var.location}"
}

provider "azuread" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

data "azurerm_resource_group" "project" {
  name     = "${local.domain}-resources"
}

/*
resource "azurerm_resource_group" "builds" {
  name     = "${local.domain}-builds-resources"
  location = "${local.location}"
}

resource "azurerm_storage_account" "builds" {
  count                    = "${local.env == "production" ? 1 : 0}"
  name                     = "${var.domain}builds"
  resource_group_name      = "${azurerm_resource_group.builds.name}"
  location                 = "${local.location}"
  account_tier             = "Standard"
  account_kind             = "BlobStorage"
  account_replication_type = "LRS"
  enable_advanced_threat_protection = true
}
*/

/*resource "azurerm_storage_account" "static_website" {
  account_replication_type  = "LRS"
  account_tier              = "Standard"
  account_kind              = "StorageV2"
  location                 = "${local.location}"
  name                      = "kk${local.env}frontend"
  resource_group_name       = "${data.azurerm_resource_group.project.name}"
  enable_https_traffic_only = true

  provisioner "local-exec" {
    command = "az storage blob service-properties update --account-name ${azurerm_storage_account.static_website.name} --static-website  --index-document index.html --404-document 404.html"
  }
}
*/