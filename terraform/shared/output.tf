output "vpc_id" {
  description = "ID of the shared VPC"
  value       = aws_vpc.veloscope_vpc.id
}

output "ecr_prepare_batch_repository_url" {
  description = "URL of the prepare-batch ECR repository"
  value       = aws_ecr_repository.prepare_batch.repository_url
}

output "ecr_upload_batch_repository_url" {
  description = "URL of the upload-batch ECR repository"
  value       = aws_ecr_repository.upload_batch.repository_url
}

output "ecr_download_batch_repository_url" {
  description = "URL of the download-batch ECR repository"
  value       = aws_ecr_repository.download_batch.repository_url
}