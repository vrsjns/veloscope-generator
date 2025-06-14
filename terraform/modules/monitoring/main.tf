resource "aws_cloudwatch_metric_alarm" "batch_failure_alarm" {
  alarm_name          = "veloscope-${var.environment}-batch-failure"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FailedTaskCount"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "This alarm monitors for failed ECS tasks in the Veloscope batch cluster"
  alarm_actions       = [aws_sns_topic.batch_alerts.arn]
  ok_actions          = [aws_sns_topic.batch_alerts.arn]

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_cpu_alarm" {
  alarm_name          = "veloscope-${var.environment}-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = var.cpu_threshold
  alarm_description   = "This alarm monitors for high CPU utilization in the Veloscope batch cluster"
  alarm_actions       = [aws_sns_topic.batch_alerts.arn]
  ok_actions          = [aws_sns_topic.batch_alerts.arn]

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_cloudwatch_metric_alarm" "high_memory_alarm" {
  alarm_name          = "veloscope-${var.environment}-high-memory"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = var.memory_threshold
  alarm_description   = "This alarm monitors for high memory utilization in the Veloscope batch cluster"
  alarm_actions       = [aws_sns_topic.batch_alerts.arn]
  ok_actions          = [aws_sns_topic.batch_alerts.arn]

  dimensions = {
    ClusterName = var.cluster_name
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_cloudwatch_dashboard" "batch_dashboard" {
  dashboard_name = "veloscope-${var.environment}-batch"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", var.cluster_name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "CPU Utilization"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ClusterName", var.cluster_name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Memory Utilization"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "RunningTaskCount", "ClusterName", var.cluster_name],
            ["AWS/ECS", "PendingTaskCount", "ClusterName", var.cluster_name],
            ["AWS/ECS", "FailedTaskCount", "ClusterName", var.cluster_name]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Task Counts"
        }
      }
    ]
  })
}

resource "aws_sns_topic" "batch_alerts" {
  name = "veloscope-${var.environment}-batch-alerts"
  
  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_sns_topic_subscription" "email_subscription" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.batch_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}