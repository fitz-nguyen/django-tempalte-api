# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  bastion_name = "${local.domain}-bastion"
  admin_username = "${var.admin_username}"
  admin_password = "${var.admin_password}"
  location = "${var.location}"
}

provider "azurerm" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

##############################################################################
# LOG ANALYTICS
##############################################################################

data "azurerm_resource_group" "project" {
  name     = "${local.domain}-resources"
}

/*
resource "azurerm_log_analytics_workspace" "api" {
  name                = "${local.domain}-api-log-analytics"
  location            = "${data.azurerm_resource_group.project.location}"
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_automation_account" "api" {
  name                = "${local.domain}-api-automation"
  location            = "${data.azurerm_resource_group.project.location}"
  resource_group_name = "${data.azurerm_resource_group.project.name}"

  sku {
    name = "Basic"
  }

  tags = {
    environment = "${local.env}"
  }
}

resource "azurerm_log_analytics_linked_service" "api" {
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  workspace_name      = "${azurerm_log_analytics_workspace.api.name}"
  resource_id         = "${azurerm_automation_account.api.id}"
}


data "azurerm_resource_group" "db" {
  name     = "${local.domain}-resources-db"
}

resource "azurerm_log_analytics_workspace" "db" {
  name                = "${local.domain}-db-log-analytics"
  location            = "${data.azurerm_resource_group.db.location}"
  resource_group_name = "${data.azurerm_resource_group.db.name}"
  sku                 = "PerGB2018"
  retention_in_days   = 30
}
*/