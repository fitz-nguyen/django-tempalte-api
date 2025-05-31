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

data "aws_subnet" "subnet_public_b" {
  tags = {
    Name            = "subnet_public_b"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

data "aws_subnet" "subnet_public_c" {
  tags = {
    Name            = "subnet_public_c"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

data "aws_subnet_ids" "subnet_ids" {
  vpc_id = "${data.aws_vpc.vpc.id}"

  tags = {
    Name            = "subnet_public_*"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

resource "aws_security_group" "web_access" {
  name        = "${local.domain}-web_access"
  description = "web access for machine"
  vpc_id      = "${data.aws_vpc.vpc.id}"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name            = "${local.domain}-web_access"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_security_group" "ssh" {
  name        = "${local.domain}-ssh"
  description = "ssh access for machine"
  vpc_id      = "${data.aws_vpc.vpc.id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [
        "64.30.97.205/32",
        "113.161.61.248/32",
        "0.0.0.0/0"
      ]
  }

  tags = {
    Name            = "${local.domain}-ssh"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_security_group" "sg_elb" {
  name        = "${local.domain}-elb"
  description = "web access for machine"
  vpc_id      = "${data.aws_vpc.vpc.id}"

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

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }

  tags = {
    Name            = "${local.domain}-elb"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "tls_private_key" "private_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "key_pair" {
  key_name   = "${local.env}"
  public_key = "${tls_private_key.private_key.public_key_openssh}"
}


resource "aws_instance" "aws_instance_api" {
  ami                         = "${local.ubuntu_ami}"
  instance_type               = "t3.small"
  key_name                    = "${aws_key_pair.key_pair.key_name}"
  subnet_id                   = "${data.aws_subnet.subnet_public_b.id}"
  disable_api_termination     = "${local.env == "production" ? true : false}"
  monitoring                  = "true"
  associate_public_ip_address = "true"

  root_block_device {
    volume_size = "20"
  }

  vpc_security_group_ids = ["${aws_security_group.web_access.id}", "${data.aws_security_group.sg.id}", "${aws_security_group.ssh.id}"]

  tags = {
    Name            = "${local.domain}-api"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }

  timeouts {
    create = "20m"
  }
}


resource "aws_alb_target_group_attachment" "aws_instance_api" {
  target_group_arn = "${aws_alb_target_group.back_end.arn}"
  target_id        = "${aws_instance.aws_instance_api.id}"
  port             = 80
}

/*
resource "aws_eip" "master_instance_eip" {
  instance   = "${aws_instance.aws_instance_api.id}"
  depends_on = ["aws_instance.aws_instance_api"]
  vpc        = true
}

output "master_instance_eip" {
  value = "${aws_eip.master_instance_eip.public_ip}"
}
*/

/*
resource "aws_elb" "elb" {
  name               = "${local.env}-elb"
  subnets            = ["${data.aws_subnet_ids.subnet_ids.ids}"]
  security_groups    = ["${aws_security_group.sg_elb.id}"]


  listener {
    instance_port     = 80
    instance_protocol = "http"
    lb_port           = 80
    lb_protocol       = "http"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }

  instances                   = ["${aws_instance.aws_instance_api.id}"]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags = {
    Name = "${local.domain}-elb"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}
*/

### ALB

resource "aws_alb" "back_end" {
  name            = "${local.domain}-alb-be"
  subnets         = ["${data.aws_subnet.subnet_public_b.id}","${data.aws_subnet.subnet_public_c.id}"]
  security_groups = ["${aws_security_group.sg_elb.id}"]
  enable_deletion_protection       = true
  idle_timeout                     = 400
  enable_http2                     = true

  tags = {
    Name = "${local.domain}-alb"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_alb_target_group" "back_end" {
  name        = "${local.domain}-alb-be"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = "${data.aws_vpc.vpc.id}"
  target_type = "instance"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 60
    path                = "/docs/"
    protocol            = "HTTP"
    port                = 80
    interval            = 120
    matcher             = "200"
  }
}

# Redirect all traffic from the ALB to the target group
resource "aws_alb_listener" "back_end" {
  load_balancer_arn = "${aws_alb.back_end.id}"
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = "${var.frontend_cert_arn}"

  default_action {
    target_group_arn = "${aws_alb_target_group.back_end.id}"
    type             = "forward"
  }
}




/*
resource "aws_placement_group" "back_end" {
  name     = "${local.domain}-back_end"
  strategy = "cluster"
}

resource "aws_lb" "back_end" {
  name               = "${local.env}-elb"
  security_groups    = ["${aws_security_group.sg_elb.id}"]
  subnets            = ["${data.aws_subnet.subnet_public_b.id}","${data.aws_subnet.subnet_public_c.id}"]
  load_balancer_type = "application"
  enable_deletion_protection = true

  idle_timeout                     = 400
  enable_http2                     = true

  tags = {
    Name = "${local.domain}-elb"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
    Version         = "${var.tag_version}"
    Strategy        = "${var.tag_strategy}"
  }
}

resource "aws_lb_target_group" "back_end" {
  name     = "${local.env}-lb-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = "${data.aws_vpc.vpc.id}"
  target_type = "ip"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    path                = "/docs/"
    protocol            = "HTTP"
    port                = 80
    path                = "/docs/"
    interval            = 30
    matcher             = "200"
  }
}
*/


/*
resource "aws_lb_listener" "front_end_https" {
  load_balancer_arn = "${aws_lb.back_end.arn}"
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = "${var.frontend_cert_arn}"

  default_action {
    type             = "forward"
    target_group_arn = "${aws_alb_target_group.back_end.arn}"
  }
}
*/



