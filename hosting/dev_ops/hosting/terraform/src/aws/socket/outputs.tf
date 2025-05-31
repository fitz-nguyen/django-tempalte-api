

output "api_public_ip" {
  # value = "${aws_instance.aws_instance_api.public_ip}"
  value = "N/A"
}

output elb_dns_name {
  value = "${data.aws_alb.elb_backend.dns_name}"
}
