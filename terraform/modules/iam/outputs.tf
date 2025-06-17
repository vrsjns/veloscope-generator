output "batch_role_arn" {
  description = "ARN of the batch role"
  value       = aws_iam_role.batch_role.arn
}

output "batch_role_name" {
  description = "Name of the batch role"
  value       = aws_iam_role.batch_role.name
}

output "events_role_arn" {
  description = "ARN of the events role"
  value       = aws_iam_role.events_role.arn
}

output "events_role_name" {
  description = "Name of the events role"
  value       = aws_iam_role.events_role.name
}
