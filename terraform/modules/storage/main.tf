# S3 bucket for storing data
resource "aws_s3_bucket" "data_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = var.bucket_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "data_bucket_versioning" {
  bucket = aws_s3_bucket.data_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_bucket_encryption" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket lifecycle configuration
resource "aws_s3_bucket_lifecycle_configuration" "data_bucket_lifecycle" {
  bucket = aws_s3_bucket.data_bucket.id

  rule {
    id     = "cleanup-old-files"
    status = "Enabled"

    # Add a filter block with an empty prefix (applies to all objects)
    filter {
      prefix = ""
    }

    expiration {
      days = 90
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}
