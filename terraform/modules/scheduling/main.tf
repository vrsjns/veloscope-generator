# CloudWatch Events Rule for prepare batch
resource "aws_cloudwatch_event_rule" "prepare_batch_schedule" {
  name                = "veloscope-${var.environment}-prepare-batch-schedule"
  description         = "Schedule for preparing batch jobs"
  schedule_expression = var.prepare_batch_schedule_expression

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# CloudWatch Events Target for prepare batch
resource "aws_cloudwatch_event_target" "prepare_batch_target" {
  rule      = aws_cloudwatch_event_rule.prepare_batch_schedule.name
  target_id = "veloscope-${var.environment}-prepare-batch"
  arn       = var.cluster_arn
  role_arn  = var.events_role_arn

  ecs_target {
    task_count          = 1
    task_definition_arn = var.prepare_batch_task_definition_arn
    launch_type         = "FARGATE"
    platform_version    = "LATEST"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [var.security_group_id]
      assign_public_ip = true
    }
  }
}

# CloudWatch Events Rule for upload batch
resource "aws_cloudwatch_event_rule" "upload_batch_schedule" {
  name                = "veloscope-${var.environment}-upload-batch-schedule"
  description         = "Schedule for uploading batch jobs"
  schedule_expression = var.upload_batch_schedule_expression

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# CloudWatch Events Target for upload batch
resource "aws_cloudwatch_event_target" "upload_batch_target" {
  rule      = aws_cloudwatch_event_rule.upload_batch_schedule.name
  target_id = "veloscope-${var.environment}-upload-batch"
  arn       = var.cluster_arn
  role_arn  = var.events_role_arn

  ecs_target {
    task_count          = 1
    task_definition_arn = var.upload_batch_task_definition_arn
    launch_type         = "FARGATE"
    platform_version    = "LATEST"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [var.security_group_id]
      assign_public_ip = true
    }
  }
}

# CloudWatch Events Rule for download batch
resource "aws_cloudwatch_event_rule" "download_batch_schedule" {
  name                = "veloscope-${var.environment}-download-batch-schedule"
  description         = "Schedule for downloading batch results"
  schedule_expression = var.download_batch_schedule_expression

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# CloudWatch Events Target for download batch
resource "aws_cloudwatch_event_target" "download_batch_target" {
  rule      = aws_cloudwatch_event_rule.download_batch_schedule.name
  target_id = "veloscope-${var.environment}-download-batch"
  arn       = var.cluster_arn
  role_arn  = var.events_role_arn

  ecs_target {
    task_count          = 1
    task_definition_arn = var.download_batch_task_definition_arn
    launch_type         = "FARGATE"
    platform_version    = "LATEST"

    network_configuration {
      subnets          = var.subnet_ids
      security_groups  = [var.security_group_id]
      assign_public_ip = true
    }
  }
}
