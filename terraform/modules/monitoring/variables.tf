variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "cpu_threshold" {
  description = "Threshold for CPU utilization alarm"
  type        = number
  default     = 80
}

variable "memory_threshold" {
  description = "Threshold for memory utilization alarm"
  type        = number
  default     = 80
}

variable "alert_email" {
  description = "Email address to send alerts to"
  type        = string
  default     = ""
}
