# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  location = "${var.location}"
}

provider "azuread" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

/*
# Create an application
resource "azuread_application" "project" {
  name = "${local.domain}-ad-application"
}

# Create a service principal
resource "azuread_service_principal" "project" {
  application_id = "${azuread_application.project.application_id}"
}
*/