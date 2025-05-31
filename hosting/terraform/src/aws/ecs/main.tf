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


data "aws_security_group" "sg_elb" {
  name = "${local.domain}-elb"

  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
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

data "aws_ecr_repository" "app" {
    name = "${local.domain}"
}
data "aws_alb" "back_end" {
    name = "${local.domain}-alb-be"
}
data "aws_alb_target_group" "back_end" {
    name = "${local.domain}-alb-be"
}

data "aws_secretsmanager_secret" "secrets" {
  name = "${local.domain}-vpc-secrets"
}

data "aws_db_instance" "db" {
  db_instance_identifier = "${local.env}${var.db_name}"
}

resource "aws_ecs_cluster" "api" {
  name = "${local.domain}-api"
}

#-------------------------------
# Roles & Policies
#-------------------------------
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${local.domain}-ecs_task_execution_role"

  assume_role_policy = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_policy_attachment" "ecs_task_execution_role" {
  name       = "${local.domain}-ecs-task-execution-policy-attachment"
  roles      = ["${aws_iam_role.ecs_task_execution_role.name}"]
  policy_arn = "${aws_iam_policy.ecs_task_execution_role.arn}"
}
resource "aws_iam_policy" "ecs_task_execution_role" {
  name        = "${local.domain}-ecs-task-execution-policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeTags",
        "ecs:CreateCluster",
        "ecs:DeregisterContainerInstance",
        "ecs:DiscoverPollEndpoint",
        "ecs:Poll",
        "ecs:RegisterContainerInstance",
        "ecs:StartTelemetrySession",
        "ecs:UpdateContainerInstancesState",
        "ecs:Submit*",
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}



/*
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = "${aws_iam_role.ecs_task_execution_role.id}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs" {
    name = "${local.domain}-ecs"
    assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF

  tags = {
    Name            = "subnet_public_c"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}
resource "aws_iam_policy_attachment" "ecs" {
  name       = "${local.domain}-ecs-policy-attachment"
  roles      = ["${aws_iam_role.ecs.name}"]
  policy_arn = "${aws_iam_policy.ecs.arn}"
}
resource "aws_iam_policy" "ecs" {
  name        = "${local.domain}-ecs-policy"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeTags",
        "ecs:CreateCluster",
        "ecs:DeregisterContainerInstance",
        "ecs:DiscoverPollEndpoint",
        "ecs:Poll",
        "ecs:RegisterContainerInstance",
        "ecs:StartTelemetrySession",
        "ecs:UpdateContainerInstancesState",
        "ecs:Submit*",
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}
*/
data "aws_kms_alias" "vpc_variables" {
  name = "alias/${local.domain}-vpc-variables"
}

#-------------------------------
# CloudWatch logging
#-------------------------------

resource "aws_cloudwatch_log_group" "nginx" {
  name              = "${local.domain}-nginx-logs"
  retention_in_days = 7
  // kms_key_id        = "${data.aws_kms_alias.vpc_variables.target_key_id}"
  tags = {
    Name            = "${local.domain}-nginx-logs"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

resource "aws_cloudwatch_log_group" "redis" {
  name              = "${local.domain}-redis-logs"
  retention_in_days = 7
  //kms_key_id        = "${data.aws_kms_alias.vpc_variables.target_key_id}"
  tags = {
    Name            = "${local.domain}-redis-logs"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "${local.domain}-api-logs"
  retention_in_days = 7
  //kms_key_id        = "${data.aws_kms_alias.vpc_variables.target_key_id}"
  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

resource "aws_cloudwatch_log_group" "pgbouncer" {
  name              = "${local.domain}-pgbouncer-logs"
  retention_in_days = 7
  //kms_key_id        = "${data.aws_kms_alias.vpc_variables.target_key_id}"
  tags = {
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}

#-------------------------------
# Web Proxy
#-------------------------------
resource "aws_ecs_task_definition" "nginx" {
  family                    = "${local.domain}-nginx"
  network_mode              = "awsvpc"
  requires_compatibilities  = ["FARGATE"]
  cpu                       = 256
  memory                    = 512
  // task_role_arn             = "${aws_iam_role.ecs.arn}"
  execution_role_arn        = "${aws_iam_role.ecs_task_execution_role.arn}"

  volume {
    name = "fs-${local.domain}-api-staticfiles"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.staticfiles.id
      root_directory          = "/usr/src/api_staticfiles"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.staticfiles.id
      }
    }
  }
  volume {
    name = "fs-${local.domain}-api-media"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.media.id
      root_directory          = "/usr/src/api_media"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.media.id
      }
    }
  }

  container_definitions = <<DEFINITION
[
  {

    "environment": [
      {
        "name": "ENVIRONMENT",
        "value": "${local.env}"
      },
      {
        "name": "API_DISCOVERY_NAMESPACE",
        "value": "development-goldfishcode-api-service-discovery.api.terraform.local"
      }
    ],
    "cpu": 256,
    "command": ["/start.sh"],
    "essential": true,
    "image": "${var.fargate_web_proxy_docker_image_uri}",
    "memory": 512,
    "memory_reservation": 512,
    "name": "nginx",
    "networkMode": "awsvpc",
    "portMappings": [
      {
          "containerPort": ${var.web_proxy_port},
          "hostPort": ${var.web_proxy_port},
          "protocol": "tcp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_cloudwatch_log_group.nginx.name}",
        "awslogs-region": "${var.region}",
        "awslogs-stream-prefix": "nginx"
      }
    },
    "requiresCompatibilities": [
       "FARGATE"
    ],
    "mountPoints": [
      {
        "containerPath": "/usr/src/api_staticfiles",
        "sourceVolume": "fs-${local.domain}-api-staticfiles"
      },
      {
        "containerPath": "/usr/src/api_media",
        "sourceVolume": "fs-${local.domain}-api-media"
      }
    ]
  }
]
DEFINITION
}

resource "aws_ecs_service" "nginx" {
  name            = "${local.domain}-nginx"
  cluster         = "${aws_ecs_cluster.api.id}"
  task_definition = "${aws_ecs_task_definition.nginx.arn}"

  # The number of instantiations of the specified task definition to place and keep running on your cluster.
  desired_count   = "${var.web_proxy_count}"

  # The launch type on which to run your service.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html
  launch_type     = "FARGATE"

  # The maximumPercent parameter represents an upper limit on the number of your service's tasks
  # that are allowed in the RUNNING or PENDING state during a deployment,
  # as a percentage of the desiredCount (rounded down to the nearest integer).
  deployment_maximum_percent = var.deployment_maximum_percent

  # The minimumHealthyPercent represents a lower limit on the number of your service's tasks
  # that must remain in the RUNNING state during a deployment,
  # as a percentage of the desiredCount (rounded up to the nearest integer).
  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent

  # If your service's tasks take a while to start and respond to Elastic Load Balancing health checks,
  # you can specify a health check grace period of up to 7,200 seconds. This grace period can prevent
  # the service scheduler from marking tasks as unhealthy and stopping them before they have time to come up.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-create-loadbalancer-rolling.html
  #health_check_grace_period_seconds = var.health_check_grace_period_seconds

  # Note that Fargate tasks do support only the REPLICA scheduling strategy.
  #
  # The replica scheduling strategy places and maintains the desired number of tasks across your cluster.
  # By default, the service scheduler spreads tasks across Availability Zones.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html#service_scheduler_replica
  scheduling_strategy = "REPLICA"

  # You can use either the version number (for example, 1.4.0) or LATEST.
  # If you specify LATEST, your tasks use the most current platform version available,
  # which may not be the most recent platform version.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html
  platform_version = var.platform_version

  network_configuration {
    security_groups = ["${data.aws_security_group.sg_elb.id}", "${data.aws_security_group.sg.id}"]
    subnets         = ["${data.aws_subnet.subnet_public_b.id}","${data.aws_subnet.subnet_public_c.id}"]
    assign_public_ip  = true
  }

  load_balancer {
    target_group_arn = "${data.aws_alb_target_group.back_end.arn}"
    container_name   = "nginx"
    container_port   = "${var.web_proxy_port}"
  }

  lifecycle {
    # Ignore any changes to that count caused externally (e.g. Application Autoscaling).
    # https://www.terraform.io/docs/providers/aws/r/ecs_service.html#ignoring-changes-to-desired-count
    ignore_changes = [desired_count]
  }
}

#-------------------------------
# REDIS DEFINITION
#-------------------------------
resource "aws_service_discovery_private_dns_namespace" "redis" {
  name        = "redis.terraform.local"
  description = "${local.domain}-redis-dns-namespace"
  vpc         = "${data.aws_vpc.vpc.id}"
}

resource "aws_service_discovery_service" "redis" {
  name = "${local.domain}-redis-service-discovery"

  dns_config {
    namespace_id   = "${aws_service_discovery_private_dns_namespace.redis.id}"
    routing_policy = "MULTIVALUE"

    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_ecs_task_definition" "redis" {
  family                    = "${local.domain}-redis"
  network_mode              = "awsvpc"
  requires_compatibilities  = ["FARGATE"]
  cpu                       = 256
  memory                    = 512
  // task_role_arn             = "${aws_iam_role.ecs.arn}"
  execution_role_arn        = "${aws_iam_role.ecs_task_execution_role.arn}"

  container_definitions = <<DEFINITION
[
  {
    "environment": [
      {
        "name": "ENVIRONMENT",
        "value": "${local.env}"
      }
    ],
    "cpu": 256,
    "image": "${var.fargate_redis_docker_image_uri}",
    "memory": 512,
    "memory_reservation": 512,
    "name": "redis",
    "networkMode": "awsvpc",
    "portMappings": [
      {
          "containerPort": ${var.redis_port},
          "hostPort": ${var.redis_port},
          "protocol": "tcp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_cloudwatch_log_group.redis.name}",
        "awslogs-region": "${var.region}",
        "awslogs-stream-prefix": "redis"
      }
    },
    "requiresCompatibilities": [
       "FARGATE"
    ]
  }
]
DEFINITION
}

resource "aws_ecs_service" "redis" {
  name            = "${local.domain}-redis"
  cluster         = "${aws_ecs_cluster.api.id}"
  task_definition = "${aws_ecs_task_definition.redis.arn}"

  # The number of instantiations of the specified task definition to place and keep running on your cluster.
  desired_count   = "${var.redis_count}"

  # The launch type on which to run your service.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html
  launch_type     = "FARGATE"

  # The maximumPercent parameter represents an upper limit on the number of your service's tasks
  # that are allowed in the RUNNING or PENDING state during a deployment,
  # as a percentage of the desiredCount (rounded down to the nearest integer).
  deployment_maximum_percent = var.deployment_maximum_percent

  # The minimumHealthyPercent represents a lower limit on the number of your service's tasks
  # that must remain in the RUNNING state during a deployment,
  # as a percentage of the desiredCount (rounded up to the nearest integer).
  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent

  # If your service's tasks take a while to start and respond to Elastic Load Balancing health checks,
  # you can specify a health check grace period of up to 7,200 seconds. This grace period can prevent
  # the service scheduler from marking tasks as unhealthy and stopping them before they have time to come up.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-create-loadbalancer-rolling.html
  #health_check_grace_period_seconds = var.health_check_grace_period_seconds

  # Note that Fargate tasks do support only the REPLICA scheduling strategy.
  #
  # The replica scheduling strategy places and maintains the desired number of tasks across your cluster.
  # By default, the service scheduler spreads tasks across Availability Zones.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html#service_scheduler_replica
  scheduling_strategy = "REPLICA"

  # You can use either the version number (for example, 1.4.0) or LATEST.
  # If you specify LATEST, your tasks use the most current platform version available,
  # which may not be the most recent platform version.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html
  platform_version = var.platform_version

  service_registries {
    registry_arn = "${aws_service_discovery_service.redis.arn}"
    container_name = "redis"
  }

  network_configuration {
    security_groups   = ["${data.aws_security_group.sg.id}"]
    subnets           = ["${data.aws_subnet.subnet_public_b.id}","${data.aws_subnet.subnet_public_c.id}"]
    assign_public_ip  = true
  }

  lifecycle {
    # Ignore any changes to that count caused externally (e.g. Application Autoscaling).
    # https://www.terraform.io/docs/providers/aws/r/ecs_service.html#ignoring-changes-to-desired-count
    ignore_changes = [desired_count]
  }
}

#-------------------------------
# API DEFINITION
#-------------------------------

resource "aws_service_discovery_private_dns_namespace" "api" {
  name        = "api.terraform.local"
  description = "${local.domain}-api-dns-namespace"
  vpc         = "${data.aws_vpc.vpc.id}"
}

resource "aws_service_discovery_service" "api" {
  name = "${local.domain}-api-service-discovery"

  dns_config {
    namespace_id   = "${aws_service_discovery_private_dns_namespace.api.id}"
    routing_policy = "MULTIVALUE"

    dns_records {
      ttl  = 10
      type = "A"
    }
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}

resource "aws_ecs_task_definition" "api" {
  family                    = "${local.domain}-api"
  network_mode              = "awsvpc"
  requires_compatibilities  = ["FARGATE"]
  cpu                       = 512
  memory                    = 1024
  // task_role_arn             = "${aws_iam_role.ecs.arn}"
  execution_role_arn        = "${aws_iam_role.ecs_task_execution_role.arn}"

  volume {
    name = "fs-${local.domain}-api-staticfiles"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.staticfiles.id
      root_directory          = "/usr/src/api_staticfiles"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.staticfiles.id
      }
    }
  }
  volume {
    name = "fs-${local.domain}-api-media"

    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.media.id
      root_directory          = "/usr/src/api_media"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.media.id
      }
    }
  }

  container_definitions = <<DEFINITION
[
  {
    "environment": [
      {
        "name": "ENVIRONMENT",
        "value": "${local.env}"
      },
      {
        "name": "BASE_URL",
        "value": "http://localhost"
      },
      {
        "name": "FRONTEND_BASE_URL",
        "value": "http://localhost"
      },
      {
        "name": "DATABASE_URL",
        "value": "${data.aws_db_instance.db.engine}://${var.db_username}:${var.db_password}@localhost:6432/${var.env}${var.db_name}"
      }
    ],
    "cpu": 256,
    "command":  ["/usr/src/api/gunicorn.sh"],
    "image": "${var.fargate_api_docker_image_uri}",
    "memory": 512,
    "memory_reservation": 512,
    "name": "api",
    "networkMode": "awsvpc",
    "essential": true,
    "portMappings": [
      {
          "containerPort": ${var.api_proxy_port},
          "hostPort": ${var.api_proxy_port},
          "protocol": "tcp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_cloudwatch_log_group.api.name}",
        "awslogs-region": "${var.region}",
        "awslogs-stream-prefix": "api"
      }
    },
    "requiresCompatibilities": [
       "FARGATE"
    ],
    "mountPoints": [
      {
        "containerPath": "/usr/src/api_staticfiles",
        "sourceVolume": "fs-${local.domain}-api-staticfiles"
      },
      {
        "containerPath": "/usr/src/api_media",
        "sourceVolume": "fs-${local.domain}-api-media"
      }
    ]
  },
  {
    "environment": [
      {
        "name": "PGBOUNCER_VERSION",
        "value": "1.14.0"
      },
      {
        "name": "DATABASES_HOST",
        "value": "${data.aws_db_instance.db.address}"
      },
      {
        "name": "DATABASES_CLIENT_SIDE_DBNAME",
        "value": "${var.env}${var.db_name}"
      },
      {
        "name": "DATABASES_DBNAME",
        "value": "${var.env}${var.db_name}"
      },
      {
        "name": "DATABASES_USER",
        "value": "${var.db_username}"
      },
      {
        "name": "DATABASES_PASSWORD",
        "value": "${var.db_password}"
      },
      {
        "name": "DATABASES_PORT",
        "value": "${data.aws_db_instance.db.port}"
      },
      {
        "name": "DATABASES_POOL_SIZE",
        "value": "20"
      },
      {
        "name": "DATABASES_POOL_MODE",
        "value": "session"
      }
    ],
    "cpu": 256,
    "image": "${var.fargate_pgbouncer_docker_image_uri}",
    "memory": 512,
    "memory_reservation": 512,
    "name": "pgbouncer",
    "networkMode": "awsvpc",
    "essential": true,
    "portMappings": [
      {
          "containerPort": ${var.pgbouncer_port},
          "hostPort": ${var.pgbouncer_port},
          "protocol": "tcp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_cloudwatch_log_group.pgbouncer.name}",
        "awslogs-region": "${var.region}",
        "awslogs-stream-prefix": "api"
      }
    },
    "requiresCompatibilities": [
       "FARGATE"
    ]
  }
]
DEFINITION
}

resource "aws_ecs_service" "api" {
  name            = "${local.domain}-api"
  cluster         = "${aws_ecs_cluster.api.id}"
  task_definition = "${aws_ecs_task_definition.api.arn}"

  # The number of instantiations of the specified task definition to place and keep running on your cluster.
  desired_count   = "${var.api_count}"

  # The launch type on which to run your service.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html
  launch_type     = "FARGATE"

  # The maximumPercent parameter represents an upper limit on the number of your service's tasks
  # that are allowed in the RUNNING or PENDING state during a deployment,
  # as a percentage of the desiredCount (rounded down to the nearest integer).
  deployment_maximum_percent = var.deployment_maximum_percent

  # The minimumHealthyPercent represents a lower limit on the number of your service's tasks
  # that must remain in the RUNNING state during a deployment,
  # as a percentage of the desiredCount (rounded up to the nearest integer).
  deployment_minimum_healthy_percent = var.deployment_minimum_healthy_percent

  # If your service's tasks take a while to start and respond to Elastic Load Balancing health checks,
  # you can specify a health check grace period of up to 7,200 seconds. This grace period can prevent
  # the service scheduler from marking tasks as unhealthy and stopping them before they have time to come up.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/service-create-loadbalancer-rolling.html
  #health_check_grace_period_seconds = var.health_check_grace_period_seconds

  # Note that Fargate tasks do support only the REPLICA scheduling strategy.
  #
  # The replica scheduling strategy places and maintains the desired number of tasks across your cluster.
  # By default, the service scheduler spreads tasks across Availability Zones.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs_services.html#service_scheduler_replica
  scheduling_strategy = "REPLICA"

  # You can use either the version number (for example, 1.4.0) or LATEST.
  # If you specify LATEST, your tasks use the most current platform version available,
  # which may not be the most recent platform version.
  # https://docs.aws.amazon.com/AmazonECS/latest/developerguide/platform_versions.html
  platform_version = var.platform_version

  service_registries {
    registry_arn = "${aws_service_discovery_service.api.arn}"
    container_name = "api"
  }

  network_configuration {
    security_groups = ["${data.aws_security_group.sg.id}"]
    subnets           = ["${data.aws_subnet.subnet_public_b.id}","${data.aws_subnet.subnet_public_c.id}"]
    assign_public_ip  = true
  }

  lifecycle {
    # Ignore any changes to that count caused externally (e.g. Application Autoscaling).
    # https://www.terraform.io/docs/providers/aws/r/ecs_service.html#ignoring-changes-to-desired-count
    ignore_changes = [desired_count]
  }
}


#-------------------------------
# EFS
#-------------------------------
resource "aws_efs_file_system" "staticfiles" {
  encrypted         = true
  kms_key_id        = "${data.aws_kms_alias.vpc_variables.target_key_arn}"
  tags = {
    Name            = "fs-${local.domain}-api-staticfiles"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}
resource "aws_efs_access_point" "staticfiles" {
  file_system_id = "${aws_efs_file_system.staticfiles.id}"
}
resource "aws_efs_mount_target" "staticfiles_public_b" {
  file_system_id  = aws_efs_file_system.staticfiles.id
  subnet_id       = data.aws_subnet.subnet_public_b.id
  security_groups = [data.aws_security_group.sg.id]
}
resource "aws_efs_mount_target" "staticfiles_public_c" {
  file_system_id = aws_efs_file_system.staticfiles.id
  subnet_id      = data.aws_subnet.subnet_public_c.id
  security_groups = [data.aws_security_group.sg.id]
}

resource "aws_efs_file_system" "media" {
  encrypted         = true
  kms_key_id        = "${data.aws_kms_alias.vpc_variables.target_key_arn}"
  tags = {
    Name            = "fs-${local.domain}-api-media"
    Domain          = "${var.domain}"
    Environment     = "${var.env}"
  }
}
resource "aws_efs_access_point" "media" {
  file_system_id = "${aws_efs_file_system.media.id}"
}
resource "aws_efs_mount_target" "media_public_b" {
  file_system_id = aws_efs_file_system.media.id
  subnet_id      = data.aws_subnet.subnet_public_b.id
  security_groups = [data.aws_security_group.sg.id]
}
resource "aws_efs_mount_target" "media_public_c" {
  file_system_id = aws_efs_file_system.media.id
  subnet_id      = data.aws_subnet.subnet_public_c.id
  security_groups = [data.aws_security_group.sg.id]
}

/*
resource "aws_appautoscaling_target" "api" {
  max_capacity       = 10
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.api.name}/${aws_ecs_cluster.api.name}"
  role_arn           = "arn:aws:iam::${local.account_id}:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = ["aws_ecs_service.api"]
}

resource "aws_appautoscaling_policy" "api" {
  name               = "${local.domain}-api-appautoscaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.api.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.api.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.api.service_namespace}"

  target_tracking_scaling_policy_configuration {
    target_value = 75

    scale_in_cooldown  = 300
    scale_out_cooldown = 300

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }

  depends_on = ["aws_appautoscaling_target.api"]
}
*/