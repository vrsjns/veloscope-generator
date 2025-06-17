output "sns_topic_arn" {
  description = "ARN of the SNS topic for batch alerts"
  value       = aws_sns_topic.batch_alerts.arn
}

output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.batch_dashboard.dashboard_name
}
