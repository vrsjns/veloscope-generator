# Output values
output "batch_cluster_name" {
  description = "Name of the ECS cluster for batch processing"
  value       = module.ecs.cluster_name
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for storing data"
  value       = module.storage.bucket_id
}

output "prepare_batch_task_definition" {
  description = "ARN of the prepare batch task definition"
  value       = module.ecs.prepare_batch_task_definition_arn
}

output "upload_batch_task_definition" {
  description = "ARN of the upload batch task definition"
  value       = module.ecs.upload_batch_task_definition_arn
}

output "download_batch_task_definition" {
  description = "ARN of the download batch task definition"
  value       = module.ecs.download_batch_task_definition_arn
}