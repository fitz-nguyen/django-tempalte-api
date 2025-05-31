# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  domain_short_name = "${local.env}-${var.domain_short_name}"
  bastion_name = "${local.domain}-bastion"
  admin_username = "${var.admin_username}"
  admin_password = "${var.admin_password}"
  api_username = "${var.api_username}"
  api_password = "${var.api_password}"
  // jenkins_name = "${local.domain}-jenkins"
  // jenkins_admin_username = "${var.jenkins_admin_username}"
  // jenkins_admin_password = "${var.jenkins_admin_password}"
  // public_ssh_key = "${tls_private_key.project.public_key_openssh}"
  location = "${var.location}"
}

provider "azurerm" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

##############################################################################
# VIRTUAL MACHINES
##############################################################################

data "azurerm_resource_group" "project" {
  name     = "${local.domain}-resources"
}

data "azurerm_subnet" "public" {
  name = "${local.domain}-subnet_public"
  virtual_network_name = "${local.domain}"
  resource_group_name  = "${local.domain}-resources"
}

data "azurerm_key_vault" "keyvault" {
  name                        = "${local.domain_short_name}-vault"
  resource_group_name         = "${data.azurerm_resource_group.project.name}"
}
data "azurerm_key_vault_secret" "cert" {
  name         = "${local.domain}-cert"
  key_vault_id = "${data.azurerm_key_vault.keyvault.id}"
}

/*
resource "tls_private_key" "project" {
  algorithm = "RSA"
  rsa_bits  = "2048"
}

output "public_key" {
  value = "${tls_private_key.project.private_key_pem}"
}
*/

/*
data "azurerm_log_analytics_workspace" "project" {
  name                = "${local.domain}-api-log-analytics"
  resource_group_name = "${data.azurerm_resource_group.project.name}"
}
*/

##############################################################################
# BASTION
##############################################################################

/*
resource "azurerm_resource_group" "bastion" {
  count = "${local.env == "production" ? 0 : 1}"
  name     = "${local.domain}-acceptanceResourceGroup1"
  location = "${local.location}"
}
resource "azurerm_network_interface" "bastion" {
  count                     = "${local.env == "production" ? 0 : 1}"
  name                      = "${azurerm_resource_group.bastion.name}-nic"
  location                  = "${azurerm_resource_group.bastion.location}"
  resource_group_name       = "${azurerm_resource_group.bastion.name}"
  network_security_group_id = "${azurerm_network_security_group.bastion.id}"

  ip_configuration {
    name                          = "internal"
    subnet_id                     = "${data.azurerm_subnet.public.id}"
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = "${azurerm_public_ip.bastion.id}"
  }
}

resource "azurerm_public_ip" "bastion" {
  count               = "${local.env == "production" ? 0 : 1}"
  name                = "${local.domain}-bastionpip"
  location            = "${azurerm_resource_group.bastion.location}"
  resource_group_name = "${azurerm_resource_group.bastion.name}"
  allocation_method   = "Dynamic"
}

output "bastion_public_ip" {
  value = "${azurerm_public_ip.bastion.*.ip_address}"
}

resource "azurerm_network_security_group" "bastion" {
  count               = "${local.env == "production" ? 0 : 1}"
  name                = "${local.domain}-jboxnsg"
  location            = "${local.location}"
  resource_group_name = "${azurerm_resource_group.bastion.name}"

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "64.30.97.205/32"    # add source addr
    destination_address_prefix = "*"
  }
}

resource "azurerm_virtual_machine" "bastion" {
  count                 = "${local.env == "production" ? 0 : 1}"
  name                  = "bastion"
  location              = "${azurerm_resource_group.bastion.location}"
  resource_group_name   = "${azurerm_resource_group.bastion.name}"
  network_interface_ids = ["${azurerm_network_interface.bastion.id}"]
  vm_size               = "Standard_F2"

  delete_os_disk_on_termination = true

  delete_data_disks_on_termination = true

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "${local.bastion_name}-osdisk"
    managed_disk_type = "Standard_LRS"
    caching           = "ReadWrite"
    create_option     = "FromImage"
  }

  os_profile {
    computer_name  = "${local.bastion_name}"
    admin_username = "${local.admin_username}"
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      path     = "/home/${local.admin_username}/.ssh/authorized_keys"
      key_data = "${local.public_ssh_key}"
    }
  }
}
*/

/*
resource "azurerm_virtual_machine_extension" "bastion-disk-encrypt" {
  name                       = "${local.env}-bastion-disk-encrypt"
  location                   = "${azurerm_resource_group.bastion.location}"
  resource_group_name        = "${azurerm_resource_group.bastion.name}"
  virtual_machine_name       = "${azurerm_virtual_machine.bastion.name}"
  publisher                  = "Microsoft.Azure.Security"
  type                       = "AzureDiskEncryptionForLinux"
  type_handler_version       = "1.1"
  auto_upgrade_minor_version = true

  settings = <<SETTINGS
    {
        "EncryptionOperation": "EnableEncryption",
        "KeyVaultURL": "${data.azurerm_key_vault.keyvault.vault_uri}",
        "KeyVaultResourceId": "${data.azurerm_key_vault.keyvault.id}",
        "KekVaultResourceId": "${data.azurerm_key_vault.keyvault.id}",
        "KeyEncryptionAlgorithm": "${var.key_store_encryption}",
        "VolumeType": "All"
    }
  SETTINGS
}
*/


/*
resource "azurerm_virtual_machine_extension" "bastion" {
  name                 = "omsagent"
  location             = "${azurerm_resource_group.bastion.location}"
  resource_group_name  = "${azurerm_resource_group.bastion.name}"
  virtual_machine_name = "${azurerm_virtual_machine.bastion.name}"
  publisher            = "Microsoft.EnterpriseCloud.Monitoring"
  type                 = "MicrosoftMonitoringAgent"
  type_handler_version = "1.0"

  settings = <<SETTINGS
        {
          "workspaceId": "${data.azurerm_log_analytics_workspace.project.workspace_id}"
        }
        SETTINGS

  protected_settings = <<PROTECTED_SETTINGS
        {
          "workspaceKey": "${data.azurerm_log_analytics_workspace.project.secondary_shared_key}"
        }
        PROTECTED_SETTINGS
}
*/

##############################################################################
# JENKINS
##############################################################################

/*
resource "azurerm_resource_group" "jenkins" {
  count = "${local.env == "development" ? 1 : 0}"
  name     = "${local.domain}-jenkins"
  location = "${local.location}"
}
resource "azurerm_network_interface" "jenkins" {
  count                     = "${local.env == "development" ? 1 : 0}"
  name                      = "${azurerm_resource_group.jenkins.name}-nic"
  location                  = "${azurerm_resource_group.jenkins.location}"
  resource_group_name       = "${azurerm_resource_group.jenkins.name}"
  network_security_group_id = "${azurerm_network_security_group.jenkins.id}"

  ip_configuration {
    name                          = "internal"
    subnet_id                     = "${data.azurerm_subnet.public.id}"
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = "${azurerm_public_ip.jenkins.id}"
  }
}

resource "azurerm_public_ip" "jenkins" {
  count               = "${local.env == "development" ? 1 : 0}"
  name                = "${local.domain}-jenkinspip"
  location            = "${azurerm_resource_group.jenkins.location}"
  resource_group_name = "${azurerm_resource_group.jenkins.name}"
  allocation_method   = "Dynamic"
}

resource "azurerm_network_security_group" "jenkins" {
  count               = "${local.env == "development" ? 1 : 0}"
  name                = "${local.domain}-jenkins"
  location            = "${local.location}"
  resource_group_name = "${azurerm_resource_group.jenkins.name}"

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"    # add source addr
    destination_address_prefix = "*"
  }
}

resource "azurerm_virtual_machine" "bastion" {
  count                 = "${local.env == "development" ? 1 : 0}"
  name                  = "jenkins"
  location              = "${azurerm_resource_group.jenkins.location}"
  resource_group_name   = "${azurerm_resource_group.jenkins.name}"
  network_interface_ids = ["${azurerm_network_interface.jenkins.id}"]
  vm_size               = "Standard_F2"

  storage_image_reference {
    publisher = "MicrosoftOSTC"
    offer     = "FreeBSD"
    sku       = "11.1"
    version   = "latest"
  }

  storage_os_disk {
    name              = "${local.bastion_name}-osdisk"
    managed_disk_type = "Standard_LRS"
    caching           = "ReadWrite"
    create_option     = "FromImage"
  }

  os_profile {
    computer_name  = "${local.jenkins_name}"
    admin_username = "${local.jenkins_admin_username}"
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      path     = "/home/${local.jenkins_admin_username}/.ssh/authorized_keys"
      key_data = "${local.public_ssh_key}"
    }
  }
}
*/

##############################################################################
# API
##############################################################################

resource "azurerm_network_security_group" "api" {
  name                = "${local.domain}-api"
  location            = "${local.location}"
  resource_group_name = "${data.azurerm_resource_group.project.name}"

  security_rule {
    name                       = "web"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "ssh"
    priority                   = 1000
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefixes    = ["0.0.0.0/0"]
    /*
    source_address_prefixes    = [
        "64.30.97.205/32",
        "123.21.69.248/32",
        "113.161.61.248/32",
        "96.231.242.240/32"
      ]
      */
    destination_address_prefix = "*"
  }
}

resource "azurerm_public_ip" "apipip" {
  count                        = "${var.api_count}"
  name                         = "${format("%s-api-pip-%03d", local.domain, count.index + 1)}"
  location                     = "${var.location}"
  resource_group_name          = "${data.azurerm_resource_group.project.name}"
  allocation_method            = "Static"
  sku                          = "Standard" # "Standard"
}

resource "azurerm_network_interface" "api" {
  count                     = "${var.api_count}"
  name                      = "${format("%s-api-nic-%03d", local.domain, count.index + 1)}"
  location                  = "${local.location}"
  resource_group_name       = "${data.azurerm_resource_group.project.name}"
  network_security_group_id = "${azurerm_network_security_group.api.id}"

  ip_configuration {
    name                          = "${format("%s-api-nic-config-%03d", local.domain, count.index + 1)}"
    subnet_id                     = "${data.azurerm_subnet.public.id}"
    #private_ip_address_allocation = "dynamic"
    private_ip_address_allocation = "Static"
    private_ip_address            = "${format("${var.subnet["subnet_public.cidr_block.ip_mask"]}", count.index + 20)}"
    public_ip_address_id          = "${azurerm_public_ip.apipip.*.id[count.index]}"

    #load_balancer_backend_address_pools_ids = ["${azurerm_lb_backend_address_pool.flbbackendpool.id}"]
    #load_balancer_inbound_nat_rules_ids = ["${azurerm_lb_nat_rule.lbnatrule.*.id[count.index]}"]
  }
}

output "api_private_ip" {
  value = "${azurerm_network_interface.api.*.private_ip_address}"
}
output "api_public_ip" {
  value = "${azurerm_public_ip.apipip.*.ip_address}"
}



# IP Address for Jenkins access

/*
resource "azurerm_network_security_group" "apipip" {
  name                = "${local.domain}-api-pip"
  location            = "${local.location}"
  resource_group_name = "${data.azurerm_resource_group.project.name}"

  security_rule {
    name                       = "ssh"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefixes    = [
        "64.30.97.205/32",
        "123.21.69.248/32",
        "113.161.61.248/32",
        "96.231.242.240/32"
      ]
    destination_address_prefix = "*"
  }

}

resource "azurerm_public_ip" "apipip" {
  count                        = "${var.api_count}"
  name                         = "${format("%s-api-pip-%03d", local.domain, count.index + 1)}"
  location                     = "${var.location}"
  resource_group_name          = "${data.azurerm_resource_group.project.name}"
  allocation_method            = "Static"
  sku                          = "Standard" # "Standard"
}

resource "azurerm_network_interface" "apipip" {
  count                     = "${var.api_count}"
  name                      = "${format("%s-api-pip-nic-%03d", local.domain, count.index + 1)}"
  location                  = "${data.azurerm_resource_group.project.location}"
  resource_group_name       = "${data.azurerm_resource_group.project.name}"
  network_security_group_id = "${azurerm_network_security_group.apipip.id}"

  ip_configuration {
    name                          = "external"
    subnet_id                     = "${data.azurerm_subnet.public.id}"
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = "${azurerm_public_ip.apipip.*.id[count.index]}"
  }
}
*/





resource "azurerm_availability_set" "api" {
  name                        = "${local.domain}-webavset"
  location                    = "${local.location}"
  resource_group_name         = "${data.azurerm_resource_group.project.name}"
  managed                     = "true"
  platform_fault_domain_count = 2 # default 3 not working in some regions like Korea
}

/*
data "azurerm_image" "api" {
  name                = "${var.api_custom_image_name}"
  resource_group_name = "${var.api_custom_image_resource_group}"
}
*/

resource "azurerm_virtual_machine" "api" {
  count                 = "${var.api_count}"
  name                  = "${format("%s-api-%03d", local.domain, count.index + 1)}"
  location              = "${local.location}"
  resource_group_name   = "${data.azurerm_resource_group.project.name}"
  network_interface_ids = ["${azurerm_network_interface.api.*.id[count.index]}"]
  primary_network_interface_id = "${azurerm_network_interface.api.*.id[count.index]}"
  vm_size               = "${var.api_vmsize}"
  availability_set_id   = "${azurerm_availability_set.api.id}"

  delete_os_disk_on_termination = true

  delete_data_disks_on_termination = true

/*
  storage_image_reference {
    id = "${data.azurerm_image.api.id}"
  }
*/

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "${format("%s-api-%03d-osdisk", local.domain, count.index + 1)}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
    disk_size_gb      = "40"
  }
  os_profile {
    computer_name  = "${format("tfapivm%03d", count.index + 1)}"
    admin_username = "${local.api_username}"
    admin_password = "${local.api_password}"
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }

  tags = {
    name = "${format("%s-api", local.domain)}"
  }

}

/*
resource "azurerm_virtual_network_peering" "api" {
  name                      = "${local.domain}-peer-jenkins"
  resource_group_name       = "${data.azurerm_resource_group.project.name}"
  virtual_network_name      = "${azurerm_network_security_group.api.azurerm_virtual_network.name}"
  remote_virtual_network_id = "${azurerm_network_security_group.jenkins.azurerm_virtual_network.name}"
}
*/

##############################################################################
# API APPLICATION GATEWAY
##############################################################################

resource "azurerm_subnet" "appgateway" {
  name = "${local.domain}-subnet_api_appgateway"
  virtual_network_name = "${local.domain}"
  resource_group_name  = "${local.domain}-resources"
  address_prefix       = "${var.subnet["subnet_api_appgateway.cidr_block"]}"
}

resource "azurerm_public_ip" "appgwpip" {
  name                         = "${local.domain}-appgwpip"
  domain_name_label            = "${local.domain}"
  location                     = "${var.location}"
  resource_group_name          = "${data.azurerm_resource_group.project.name}"
  allocation_method            = "Dynamic"
  idle_timeout_in_minutes      = 30
}

resource "azurerm_application_gateway" "network" {
  name                = "${local.domain}-appgateway"
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  location            = "${data.azurerm_resource_group.project.location}"

  sku {
    name     = "Standard_Small"
    tier     = "Standard"
    capacity = 1
  }
/* uncomment for WAF support (higher price)
  sku {
    name     = "WAF_v2"
    tier     = "WAF_v2"
    capacity = 2
  }

  waf_configuration {
    enabled          = "true"
    firewall_mode    = "Detection"
    rule_set_type    = "OWASP"
    rule_set_version = "3.0"
  }
*/

  gateway_ip_configuration {
    name      = "${local.domain}-appgateway-ip-configuration"
    subnet_id = "${azurerm_subnet.appgateway.id}"
  }

  frontend_port {
    name = "HTTPS"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "${local.domain}-appgateway-fe-ip-configuration"
    public_ip_address_id = "${azurerm_public_ip.appgwpip.id}"
  }

  backend_address_pool {
    name = "${local.domain}-appgateway-be-address-pool"
    ip_addresses = ["${azurerm_network_interface.api.*.private_ip_address}"]
  }

  backend_http_settings {
    name                  = "${local.domain}-appgateway-be-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "http"
    request_timeout       = 60
    probe_name            = "probe"
  }


  #http_listener {
  #  name                           = "${local.domain}-appgateway-http-listener"
  #  frontend_ip_configuration_name = "${local.domain}-appgateway-fe-ip-configuration"
  #  frontend_port_name             = "${local.domain}-appgateway-web"
  #  protocol                       = "Http"
  #}

  http_listener {
    name                           = "${local.domain}-appgateway-https-listener"
    frontend_ip_configuration_name = "${local.domain}-appgateway-fe-ip-configuration"
    frontend_port_name             = "HTTPS"
    ssl_certificate_name           = "${var.ssl_name}"
    protocol                       = "https"
  }
  ssl_certificate {
    name = "${var.ssl_name}"
    data = "${data.azurerm_key_vault_secret.cert.value}"
    password = "${var.ssl_password}"
  }

  #request_routing_rule {
  #  name                        = "${local.domain}-appgateway-request-routing-rule"
  #  rule_type                   = "Basic"
  #  http_listener_name          = "${local.domain}-appgateway-http-listener"
  #  backend_address_pool_name   = "${local.domain}-appgateway-be-address-pool"
  #  backend_http_settings_name  = "${local.domain}-appgateway-be-http-settings"
  #}

  request_routing_rule {
    name                        = "${local.domain}-appgateway-request-https-routing-rule"
    rule_type                   = "Basic"
    http_listener_name          = "${local.domain}-appgateway-https-listener"
    backend_address_pool_name   = "${local.domain}-appgateway-be-address-pool"
    backend_http_settings_name  = "${local.domain}-appgateway-be-http-settings"
  }

  probe {
    name                = "probe"
    protocol            = "http"
    host                = "127.0.0.1"
    path                = "/docs"
    interval            = "30"
    timeout             = "30"
    unhealthy_threshold = "3"
  }
}

output "appgw_ip_address" {
  value = "${azurerm_public_ip.appgwpip.ip_address}"
}

##############################################################################
# LOAD BALANCER
##############################################################################

/*
resource "azurerm_public_ip" "flbpip" {
  name                         = "${local.domain}-flbpip"
  location                     = "${var.location}"
  resource_group_name          = "${data.azurerm_resource_group.project.name}"
  public_ip_address_allocation = "static"
  sku                          = "Basic" # "Standard"
}

resource "azurerm_lb" "flb" {
  name                = "${local.domain}lb"
  location            = "${var.location}"
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  sku                 = "Basic" # "Standard"

  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = "${azurerm_public_ip.flbpip.id}"
  }
}

resource "azurerm_lb_backend_address_pool" "flbbackendpool" {
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  loadbalancer_id     = "${azurerm_lb.flb.id}"
  name                = "BackEndAddressPool"
}

resource "azurerm_lb_nat_rule" "lbnatrule" {
  count                          = "${var.api_count}"
  resource_group_name            = "${data.azurerm_resource_group.project.name}"
  loadbalancer_id                = "${azurerm_lb.flb.id}"
  name                           = "ssh-${count.index}"
  protocol                       = "tcp"
  frontend_port                  = "5000${count.index + 1}"
  backend_port                   = 22
  frontend_ip_configuration_name = "PublicIPAddress"  # "${azurerm_lb.tflb.frontend_ip_configuration.name}" not working
}

resource "azurerm_lb_rule" "lb_rule" {
  resource_group_name            = "${data.azurerm_resource_group.project.name}"
  loadbalancer_id                = "${azurerm_lb.flb.id}"
  name                           = "LBRule"
  protocol                       = "tcp"
  frontend_port                  = 80
  backend_port                   = 80
  frontend_ip_configuration_name = "PublicIPAddress"
  enable_floating_ip             = false
  backend_address_pool_id        = "${azurerm_lb_backend_address_pool.flbbackendpool.id}"
  idle_timeout_in_minutes        = 5
  probe_id                       = "${azurerm_lb_probe.lb_probe.id}"
  depends_on                     = ["azurerm_lb_probe.lb_probe"]
}

resource "azurerm_lb_probe" "lb_probe" {
  resource_group_name = "${data.azurerm_resource_group.project.name}"
  loadbalancer_id     = "${azurerm_lb.flb.id}"
  name                = "tcpProbe"
  protocol            = "tcp"
  port                = 80
  interval_in_seconds = 5
  number_of_probes    = 2
}

output "weblb_pip" {
  value = "${azurerm_public_ip.flbpip.*.ip_address}"
}
*/
