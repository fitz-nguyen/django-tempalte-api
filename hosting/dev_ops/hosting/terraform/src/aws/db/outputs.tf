output "address" {
  value = "${aws_db_instance.db.address}"
}
output "database" {
  value = "${local.env}${local.db_name}"
}
output "username" {
  value = "${aws_db_instance.db.username}"
}
output "password" {
  value = "${local.db_password}"
}