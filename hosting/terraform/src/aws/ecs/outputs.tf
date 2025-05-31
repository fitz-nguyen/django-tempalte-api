
output aws_ecs_cluster {
  value = "${aws_ecs_cluster.api.name}"
}
output "aws_nginx_ecs_task_definition" {
  value = "${aws_ecs_task_definition.nginx.family}"
}
output aws_nginx_ecs_service {
  value = "${aws_ecs_service.nginx.name}"
}
output aws_redis_ecs_service {
  value = "${aws_ecs_service.redis.name}"
}

output "aws_api_ecs_task_definition" {
  value = "${aws_ecs_task_definition.api.family}"
}
output "aws_api_ecs_discovery_namespace" {
  value = "${aws_service_discovery_private_dns_namespace.api.name}"
}

output aws_api_ecs_service {
  value = "${aws_ecs_service.api.name}"
}

output "aws_redis_ecs_task_definition" {
  value = "${aws_ecs_task_definition.redis.family}"
}