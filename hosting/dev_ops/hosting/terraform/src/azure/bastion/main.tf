# check for presence of all config variables
locals {
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  bastion_name = "${local.domain}-bastion"
  admin_username = "${var.admin_username}"
  admin_password = "${var.admin_password}"
  api_username = "${var.api_username}"
  api_password = "${var.api_password}"
  // jenkins_name = "${local.domain}-jenkins"
  // jenkins_admin_username = "${var.jenkins_admin_username}"
  // jenkins_admin_password = "${var.jenkins_admin_password}"
  public_ssh_key = "${tls_private_key.bastion.public_key_openssh}"
  location = "${var.location}"
}

provider "azurerm" {
  subscription_id = "${var.subscription_id}"
}

terraform {
  backend "azurerm" {}
}

##############################################################################
# BASTION
##############################################################################

data "azurerm_resource_group" "bastion" {
  name     = "${local.domain}-resources"
}

resource "azurerm_network_interface" "bastion" {
  name                      = "${local.domain}-bastion-nic"
  location                  = "${data.azurerm_resource_group.bastion.location}"
  resource_group_name       = "${data.azurerm_resource_group.bastion.name}"
  network_security_group_id = "${azurerm_network_security_group.bastion.id}"

  ip_configuration {
    name                          = "internal"
    subnet_id                     = "${data.azurerm_subnet.bastion.id}"
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = "${azurerm_public_ip.bastion.id}"
  }
}

resource "azurerm_public_ip" "bastion" {
  name                = "${local.domain}-bastion-pip"
  location            = "${data.azurerm_resource_group.bastion.location}"
  resource_group_name = "${data.azurerm_resource_group.bastion.name}"
  allocation_method   = "Dynamic"
}

output "bastion_public_ip" {
  value = "${azurerm_public_ip.bastion.*.ip_address}"
}

data "azurerm_subnet" "bastion" {
  name                      = "${local.domain}-subnet_public"
  resource_group_name       = "${data.azurerm_resource_group.bastion.name}"
  virtual_network_name      = "${local.domain}"
}

resource "azurerm_network_security_group" "bastion" {
  name                = "${local.domain}-bastion-sg"
  location            = "${local.location}"
  resource_group_name = "${data.azurerm_resource_group.bastion.name}"

  security_rule {
    name                       = "SSH"
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
      ]   # add source addr
    destination_address_prefix = "*"
  }
}

resource "tls_private_key" "bastion" {
  algorithm = "RSA"
  rsa_bits  = "2048"
}

output "public_key" {
  value = "${tls_private_key.bastion.private_key_pem}"
}

resource "azurerm_virtual_machine" "bastion" {
  name                  = "${local.domain}-bastion"
  location              = "${data.azurerm_resource_group.bastion.location}"
  resource_group_name   = "${data.azurerm_resource_group.bastion.name}"
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
    name              = "${local.domain}-bastion-osdisk"
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
