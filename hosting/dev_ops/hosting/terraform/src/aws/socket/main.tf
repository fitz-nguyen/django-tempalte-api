locals {
  account_id = "${var.account_id}"
  ssh_key_name = "${var.ssh_key_name}"
  env = "${var.env}"
  domain = "${local.env}-${var.domain}"
  ubuntu_ami   = "${var.ubuntu_ami}"
}

provider "aws" {
  region = "${var.region}"
  profile = "${var.profile}"
}

terraform {
  backend "s3" {}
}

data "aws_vpc" "vpc" {
  tags = {
    Name            = "${local.domain}-vpc"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

data "aws_subnet" "subnet_public_b" {
  tags = {
    Name            = "${local.domain}-subnet-public-b"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

data "aws_subnet" "subnet_public_c" {
  tags = {
    Name            = "${local.domain}-subnet-public-c"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

data "aws_alb" "elb_backend" {
  tags = {
    Name    = "${local.domain}-alb"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

data "aws_security_group" "sg" {
  name = "${local.domain}-sg"

  tags = {
    Name            = "${local.domain}-sg"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_security_group" "socket" {
  name        = "${local.domain}-ws-sg"
  description = "ssh access for machine"
  vpc_id      = "${data.aws_vpc.vpc.id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name            = "${local.domain}-ws-sg"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_instance" "aws_instance_ws" {
  ami                         = "${local.ubuntu_ami}"
  instance_type               = "t3.small"
  key_name                    = "${local.env}"
  subnet_id                   = "${data.aws_subnet.subnet_public_b.id}"
  disable_api_termination     = "${local.env == "production" ? true : false}"
  monitoring                  = "true"
  associate_public_ip_address = "true"

  root_block_device {
    volume_size = "20"
  }

  vpc_security_group_ids = ["${aws_security_group.socket.id}", "${data.aws_security_group.sg.id}"]

  tags = {
    Name            = "${local.domain}-ws"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }

  timeouts {
    create = "20m"
  }
}

resource "aws_alb_target_group_attachment" "aws_instance_ws" {
  target_group_arn = "${aws_alb_target_group.socket.arn}"
  target_id        = "${aws_instance.aws_instance_ws.id}"
  port             = 3000
}

resource "aws_alb_target_group" "socket" {
  name        = "${local.domain}-alb-ws"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = "${data.aws_vpc.vpc.id}"
  target_type = "instance"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 60
    path                = "/"
    protocol            = "HTTP"
    port                = 3000
    interval            = 120
    matcher             = "200"
  }
}
