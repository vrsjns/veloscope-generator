variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "enable_container_insights" {
  description = "Enable Container Insights for the ECS cluster"
  type        = bool
  default     = false
}

variable "prepare_batch_cpu" {
  description = "CPU units for prepare batch task"
  type        = string
  default     = "256"
}

variable "prepare_batch_memory" {
  description = "Memory for prepare batch task"
  type        = string
  default     = "512"
}

variable "upload_batch_cpu" {
  description = "CPU units for upload batch task"
  type        = string
  default     = "256"
}

variable "upload_batch_memory" {
  description = "Memory for upload batch task"
  type        = string
  default     = "512"
}

variable "download_batch_cpu" {
  description = "CPU units for download batch task"
  type        = string
  default     = "256"
}

variable "download_batch_memory" {
  description = "Memory for download batch task"
  type        = string
  default     = "512"
}

variable "execution_role_arn" {
  description = "ARN of the ECS execution role"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of the ECS task role"
  type        = string
}

variable "prepare_batch_image_url" {
  description = "URL of the prepare batch ECR repository"
  type        = string
}

variable "upload_batch_image_url" {
  description = "URL of the upload batch ECR repository"
  type        = string
}

variable "download_batch_image_url" {
  description = "URL of the download batch ECR repository"
  type        = string
}

variable "s3_bucket_id" {
  description = "ID of the S3 bucket"
  type        = string
}

variable "openai_api_key_arn" {
  description = "ARN of the OpenAI API key in SSM Parameter Store"
  type        = string
}

variable "log_group_name" {
  description = "Name of the CloudWatch log group"
  type        = string
}