output "aws_s3_bucket_frontend_domain_name" {
  value = aws_s3_bucket.frontend.bucket_domain_name
}

output "aws_s3_bucket_api_media_domain_name" {
  value = aws_s3_bucket.api_media.bucket_domain_name
}