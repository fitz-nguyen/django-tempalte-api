# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  bastion_name = "${local.domain}-bastion"
  location = "${var.location}"
}

provider "azurerm" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

resource "azurerm_resource_group" "db" {
  name     = "${local.domain}-resources-db"
  location = "${local.location}"
}

/*
resource "azurerm_sql_server" "db" {
  name                         = "${local.domain}-db"
  resource_group_name          = "${azurerm_resource_group.db.name}"
  location                     = "${local.location}"
  version                      = "12.0"
  administrator_login          = "${var.db_username}"
  administrator_login_password = "${var.db_password}"
}

resource "azurerm_sql_firewall_rule" "db-production" {
  count               = "${local.env == "production" ? 1 : 0}"
  name                = "FirewallRule1"
  resource_group_name = "${azurerm_resource_group.db.name}"
  server_name         = "${azurerm_sql_server.db.name}"
  start_ip_address    = "10.0.32.20"
  end_ip_address      = "10.0.32.30"
}

resource "azurerm_sql_firewall_rule" "db-staging" {
  count               = "${local.env == "staging" ? 1 : 0}"
  name                = "FirewallRule1"
  resource_group_name = "${azurerm_resource_group.db.name}"
  server_name         = "${azurerm_sql_server.db.name}"
  start_ip_address    = "11.0.32.20"
  end_ip_address      = "11.0.32.30"
}

output "azurerm_sql_server_id" {
  value = "${azurerm_sql_server.db.fully_qualified_domain_name}"
}

/*
resource "azurerm_sql_active_directory_administrator" "test" {
  server_name         = "${azurerm_sql_server.test.name}"
  resource_group_name = "${azurerm_resource_group.test.name}"
  login               = "sqladmin"
  tenant_id           = "${data.azurerm_client_config.current.tenant_id}"
  object_id           = "${data.azurerm_client_config.current.service_principal_object_id}"
}
*/
/*
resource "azurerm_sql_database" "db" {
  name                = "${local.domain}-db"
  resource_group_name = "${azurerm_resource_group.db.name}"
  location            = "${local.location}"
  server_name         = "${azurerm_sql_server.db.name}"
  edition             = "${var.db_edition}"

  threat_detection_policy = {
    state                      = "Enabled"
  }

  tags = {
    environment = "${var.env}"
  }
}
*/

resource "azurerm_postgresql_server" "db" {
  name                = "${local.domain}--db"
  location            = "${azurerm_resource_group.db.location}"
  resource_group_name = "${azurerm_resource_group.db.name}"

  sku {
    name     = "B_Gen5_2"
    capacity = 2
    tier     = "Basic"
    family   = "Gen5"
  }

  storage_profile {
    storage_mb            = 5120
    backup_retention_days = 7
    geo_redundant_backup  = "Disabled"
    auto_grow             = "Enabled"
  }

  administrator_login          = "${var.db_username}"
  administrator_login_password = "${var.db_password}"
  version                      = "10"
  ssl_enforcement              = "Disabled"
}

resource "azurerm_postgresql_database" "db" {
  name                = "${local.domain}--db"
  resource_group_name = "${azurerm_resource_group.db.name}"
  server_name         = "${azurerm_postgresql_server.db.name}"
  charset             = "UTF8"
  collation           = "English_United States.1252"
}