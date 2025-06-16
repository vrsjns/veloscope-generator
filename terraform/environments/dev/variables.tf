variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-central-1"
}

variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  default     = ""
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for storing data"
  type        = string
  default     = "veloscope-dev-data"
}

variable "openai_api_key" {
  description = "OpenAI API key for generating horoscopes"
  type        = string
  sensitive   = true
}

variable "alert_email" {
  description = "Email address to send alerts to"
  type        = string
  default     = "" # Default to empty string, will be overridden by tfvars
}