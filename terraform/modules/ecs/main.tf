resource "aws_ecs_cluster" "batch_cluster" {
  name = "veloscope-${var.environment}-batch-cluster"

  setting {
    name  = "containerInsights"
    value = var.enable_container_insights ? "enabled" : "disabled"
  }

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecs_task_definition" "prepare_batch" {
  family                   = "veloscope-${var.environment}-prepare-batch"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.prepare_batch_cpu
  memory                   = var.prepare_batch_memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "prepare-batch"
      #image     = "${var.prepare_batch_image_url}:${var.environment}"
      image     = "${var.prepare_batch_image_url}:latest"
      essential = true

      environment = [
        {
          name  = "ENV"
          value = var.environment
        },
        {
          name  = "S3_BUCKET_NAME"
          value = var.s3_bucket_id
        },
        {
          name  = "CONTROL_KEY"
          value = "batch_control.json"
        },
        {
          name  = "RIDERS_FILE"
          value = "riders.json"
        },
        {
          name  = "ENABLE_FILE_LOGGING"
          value = "true"
        }
      ]

      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = var.openai_api_key_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "prepare-batch"
        }
      }
    }
  ])

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecs_task_definition" "upload_batch" {
  family                   = "veloscope-${var.environment}-upload-batch"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.upload_batch_cpu
  memory                   = var.upload_batch_memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "upload-batch"
      #image     = "${var.upload_batch_image_url}:${var.environment}"
      image     = "${var.upload_batch_image_url}:latest"
      essential = true

      environment = [
        {
          name  = "ENV"
          value = var.environment
        },
        {
          name  = "S3_BUCKET_NAME"
          value = var.s3_bucket_id
        },
        {
          name  = "CONTROL_KEY"
          value = "batch_control.json"
        },
        {
          name  = "OPENAI_COMPLETION_WINDOW"
          value = "24h"
        },
        {
          name  = "ENABLE_FILE_LOGGING"
          value = "true"
        }
      ]

      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = var.openai_api_key_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "upload-batch"
        }
      }
    }
  ])

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_ecs_task_definition" "download_batch" {
  family                   = "veloscope-${var.environment}-download-batch"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.download_batch_cpu
  memory                   = var.download_batch_memory
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn

  container_definitions = jsonencode([
    {
      name      = "download-batch"
      #image     = "${var.download_batch_image_url}:${var.environment}"
      image     = "${var.download_batch_image_url}:latest"
      essential = true

      environment = [
        {
          name  = "ENV"
          value = var.environment
        },
        {
          name  = "S3_BUCKET_NAME"
          value = var.s3_bucket_id
        },
        {
          name  = "CONTROL_KEY"
          value = "batch_control.json"
        },
        {
          name  = "HOROSCOPE_PREFIX"
          value = "horoscope"
        },
        {
          name  = "ENABLE_FILE_LOGGING"
          value = "true"
        }
      ]

      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = var.openai_api_key_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = var.log_group_name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "download-batch"
        }
      }
    }
  ])

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_security_group" "batch_sg" {
  name        = "veloscope-${var.environment}-batch-sg"
  description = "Security group for batch tasks in ${var.environment}"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "veloscope-${var.environment}-batch-sg"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}