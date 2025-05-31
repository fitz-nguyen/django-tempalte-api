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
# KEY VAULT
##############################################################################

data "azurerm_resource_group" "project" {
  name     = "${local.domain}-resources"
}

/*
resource "azurerm_key_vault" "keyvault" {
  name                        = "${local.domain}-vault"
  location                    = "${data.azurerm_resource_group.project.location}"
  resource_group_name         = "${data.azurerm_resource_group.project.name}"
  enabled_for_disk_encryption = true
  tenant_id                   = "${var.tenant_id}"

  sku_name = "standard"

}
*/

/*
resource "azurerm_key_vault_key" "key" {
  name         = "${local.domain}-certificate"
  key_vault_id = "${azurerm_key_vault.keyvault.id}"
  key_type     = "RSA"
  key_size     = 2048

  key_opts = [
    "decrypt",
    "encrypt",
    "sign",
    "unwrapKey",
    "verify",
    "wrapKey",
  ]
}
*/