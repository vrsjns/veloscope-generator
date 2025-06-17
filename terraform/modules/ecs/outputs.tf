output "cluster_arn" {
  description = "ARN of the ECS cluster"
  value       = aws_ecs_cluster.batch_cluster.arn
}

output "cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.batch_cluster.name
}

output "prepare_batch_task_definition_arn" {
  description = "ARN of the prepare batch task definition"
  value       = aws_ecs_task_definition.prepare_batch.arn
}

output "upload_batch_task_definition_arn" {
  description = "ARN of the upload batch task definition"
  value       = aws_ecs_task_definition.upload_batch.arn
}

output "download_batch_task_definition_arn" {
  description = "ARN of the download batch task definition"
  value       = aws_ecs_task_definition.download_batch.arn
}

output "batch_sg_id" {
  description = "ID of the batch security group"
  value       = aws_security_group.batch_sg.id
}
