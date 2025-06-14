variable "aws_profile" {
  description = "AWS profile to use"
  type        = string
  default     = ""
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "eu-central-1"
}

variable "ecr_repo_prefix" {
  description = "Prefix for ECR repositories"
  type        = string
  default     = "veloscope"
}