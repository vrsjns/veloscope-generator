# SNS topic for batch alerts in development
resource "aws_sns_topic" "batch_alerts" {
  name = "veloscope-${var.environment}-batch-alerts"

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# SNS subscription for email alerts
resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.batch_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch log group for batch tasks
resource "aws_cloudwatch_log_group" "batch_logs" {
  name              = "/ecs/veloscope-${var.environment}-batch"
  retention_in_days = 14

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
