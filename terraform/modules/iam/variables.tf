variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  type        = string
}

variable "openai_api_key_arn" {
  description = "ARN of the SSM parameter storing the OpenAI API key"
  type        = string
}

variable "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  type        = string
}

variable "cluster_arn" {
  description = "ARN of the ECS cluster"
  type        = string
}

variable "task_definition_arns" {
  description = "List of ARNs for the ECS task definitions"
  type        = list(string)
}
