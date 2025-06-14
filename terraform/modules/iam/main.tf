resource "aws_iam_role" "batch_role" {
  name = "veloscope-${var.environment}-batch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# IAM policy for S3 access
resource "aws_iam_policy" "s3_access_policy" {
  name        = "veloscope-${var.environment}-s3-access"
  description = "Policy for accessing the Veloscope S3 bucket in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Effect = "Allow"
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      }
    ]
  })
}

# Attach S3 policy to the batch role
resource "aws_iam_role_policy_attachment" "s3_policy_attachment" {
  role       = aws_iam_role.batch_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# IAM policy for accessing SSM parameters
resource "aws_iam_policy" "ssm_access_policy" {
  name        = "veloscope-${var.environment}-ssm-access"
  description = "Policy for accessing SSM parameters in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameters",
          "ssm:GetParameter"
        ]
        Effect   = "Allow"
        Resource = var.openai_api_key_arn
      }
    ]
  })
}

# Attach SSM policy to the batch role
resource "aws_iam_role_policy_attachment" "ssm_policy_attachment" {
  role       = aws_iam_role.batch_role.name
  policy_arn = aws_iam_policy.ssm_access_policy.arn
}

# ECS execution role policy
resource "aws_iam_policy" "ecs_execution_policy" {
  name        = "veloscope-${var.environment}-ecs-execution"
  description = "Policy for ECS execution in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "${var.log_group_arn}:*"
      },
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach execution policy to the batch role
resource "aws_iam_role_policy_attachment" "ecs_execution_attachment" {
  role       = aws_iam_role.batch_role.name
  policy_arn = aws_iam_policy.ecs_execution_policy.arn
}

# IAM role for CloudWatch Events to run ECS tasks
resource "aws_iam_role" "events_role" {
  name = "veloscope-${var.environment}-events-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# IAM policy for CloudWatch Events to run ECS tasks
resource "aws_iam_policy" "events_policy" {
  name        = "veloscope-${var.environment}-events-policy"
  description = "Policy for CloudWatch Events to run ECS tasks in ${var.environment}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "ecs:RunTask"
        Effect = "Allow"
        Resource = var.task_definition_arns
        Condition = {
          ArnLike = {
            "ecs:cluster" = var.cluster_arn
          }
        }
      },
      {
        Action   = "iam:PassRole"
        Effect   = "Allow"
        Resource = "*"
        Condition = {
          StringLike = {
            "iam:PassedToService" = "ecs-tasks.amazonaws.com"
          }
        }
      }
    ]
  })
}

# Attach events policy to the events role
resource "aws_iam_role_policy_attachment" "events_policy_attachment" {
  role       = aws_iam_role.events_role.name
  policy_arn = aws_iam_policy.events_policy.arn
}