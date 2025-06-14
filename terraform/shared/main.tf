terraform {
  backend "s3" {} # Empty configuration to be filled by -backend-config
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

# VPC for all environments
resource "aws_vpc" "veloscope_vpc" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name      = "veloscope-vpc"
    ManagedBy = "terraform"
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.veloscope_vpc.id

  tags = {
    Name      = "veloscope-igw"
    ManagedBy = "terraform"
  }
}

# ECR repositories for Docker images
resource "aws_ecr_repository" "prepare_batch" {
  name                 = "${var.ecr_repo_prefix}/prepare-batch"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    ManagedBy = "terraform"
  }
}

resource "aws_ecr_repository" "upload_batch" {
  name                 = "${var.ecr_repo_prefix}/upload-batch"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    ManagedBy = "terraform"
  }
}

resource "aws_ecr_repository" "download_batch" {
  name                 = "${var.ecr_repo_prefix}/download-batch"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    ManagedBy = "terraform"
  }
}
