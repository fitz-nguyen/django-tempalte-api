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
# VPC
##############################################################################

resource "azurerm_resource_group" "project" {
  name     = "${local.domain}-resources"
  location = "${local.location}"
}

#### IMPORTANT DO NOT DELETE RESOURCE. IT IS SHARED THROUGHOUT ENVIRONMENTS ####
/*
resource "azurerm_ddos_protection_plan" "project" {
  name                = "ddos-protection"
  resource_group_name = "${local.domain}-resource"
  location            = "${azurerm_resource_group.project.location}"
}
*/

resource "azurerm_virtual_network" "project" {
  name                = "${local.domain}"
  resource_group_name = "${azurerm_resource_group.project.name}"
  location            = "${azurerm_resource_group.project.location}"
  address_space       = ["${var.vpc_cidr_block}"]


  /*
  ddos_protection_plan {
    id     = "${azurerm_ddos_protection_plan.project.id}"
    enable = true
  }
  */

  tags = {
    Name                                  = "${local.domain}"
  }
}

resource "azurerm_subnet" "public" {
  name                 = "${local.domain}-subnet_public"
  virtual_network_name = "${azurerm_virtual_network.project.name}"
  resource_group_name  = "${azurerm_resource_group.project.name}"
  address_prefix       = "${var.subnet_public_cidr_block}"
  service_endpoints    = ["Microsoft.Sql"]
}

resource "azurerm_application_security_group" "public" {
  name                = "${local.domain}-public"
  location            = "${azurerm_resource_group.project.location}"
  resource_group_name = "${azurerm_resource_group.project.name}"
}