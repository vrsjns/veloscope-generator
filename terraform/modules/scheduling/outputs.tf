output "prepare_batch_rule_name" {
  description = "Name of the CloudWatch Events rule for prepare batch"
  value       = aws_cloudwatch_event_rule.prepare_batch_schedule.name
}

output "upload_batch_rule_name" {
  description = "Name of the CloudWatch Events rule for upload batch"
  value       = aws_cloudwatch_event_rule.upload_batch_schedule.name
}

output "download_batch_rule_name" {
  description = "Name of the CloudWatch Events rule for download batch"
  value       = aws_cloudwatch_event_rule.download_batch_schedule.name
}