variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "cluster_arn" {
  description = "ARN of the ECS cluster"
  type        = string
}

variable "events_role_arn" {
  description = "ARN of the IAM role for CloudWatch Events"
  type        = string
}

variable "prepare_batch_task_definition_arn" {
  description = "ARN of the prepare batch task definition"
  type        = string
}

variable "upload_batch_task_definition_arn" {
  description = "ARN of the upload batch task definition"
  type        = string
}

variable "download_batch_task_definition_arn" {
  description = "ARN of the download batch task definition"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the ECS tasks"
  type        = list(string)
}

variable "security_group_id" {
  description = "ID of the security group for the ECS tasks"
  type        = string
}

variable "prepare_batch_schedule_expression" {
  description = "Schedule expression for prepare batch job"
  type        = string
  default     = "cron(5 1 * * ? *)"  # Default: 1:05 AM UTC daily
}

variable "upload_batch_schedule_expression" {
  description = "Schedule expression for upload batch job"
  type        = string
  default     = "cron(15 1 * * ? *)"  # Default: 1:15 AM UTC daily
}

variable "download_batch_schedule_expression" {
  description = "Schedule expression for download batch job"
  type        = string
  default     = "cron(30 * * * ? *)"  # Default: 30 minutes past every hour
}