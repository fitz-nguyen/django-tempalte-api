output private_key_pem {
  value = nonsensitive("${tls_private_key.private_key.private_key_pem}")
}
output public_key_pem {
  value = "${tls_private_key.private_key.public_key_pem}"
}

output "api_public_ip" {
  # value = "${aws_instance.aws_instance_api.public_ip}"
  value = "N/A"
}

output elb_dns_name {
  value = "${aws_alb.back_end.dns_name}"
}