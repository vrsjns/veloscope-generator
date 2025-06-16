variable "vpc_id" {
  description = "ID of the VPC to use"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
}
