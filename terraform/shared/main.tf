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

# Public subnets for shared infrastructure
#resource "aws_subnet" "public_subnet_1" {
#  vpc_id                  = aws_vpc.veloscope_vpc.id
#  cidr_block              = "10.0.1.0/24"
#  availability_zone       = "${var.aws_region}a"
#  map_public_ip_on_launch = true
#
#  tags = {
#    Name      = "veloscope-public-subnet-1"
#    ManagedBy = "terraform"
#  }
#}

#resource "aws_subnet" "public_subnet_2" {
#  vpc_id                  = aws_vpc.veloscope_vpc.id
#  cidr_block              = "10.0.2.0/24"
#  availability_zone       = "${var.aws_region}b"
#  map_public_ip_on_launch = true
#
#  tags = {
#    Name      = "veloscope-public-subnet-2"
#    ManagedBy = "terraform"
#  }
#}

# Route table for public subnets
#resource "aws_route_table" "public_route_table" {
#  vpc_id = aws_vpc.veloscope_vpc.id
#
#  route {
#    cidr_block = "0.0.0.0/0"
#    gateway_id = aws_internet_gateway.igw.id
#  }
#
#  tags = {
#    Name      = "veloscope-public-route-table"
#    ManagedBy = "terraform"
#  }
#}

# Associate route table with public subnets
#resource "aws_route_table_association" "public_subnet_1_association" {
#  subnet_id      = aws_subnet.public_subnet_1.id
#  route_table_id = aws_route_table.public_route_table.id
#}
#
#resource "aws_route_table_association" "public_subnet_2_association" {
#  subnet_id      = aws_subnet.public_subnet_2.id
#  route_table_id = aws_route_table.public_route_table.id
#}

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

# DynamoDB table for Terraform state locking
#resource "aws_dynamodb_table" "terraform_locks" {
#  name         = "veloscope-terraform-locks"
#  billing_mode = "PAY_PER_REQUEST"
#  hash_key     = "LockID"
#  
#  attribute {
#    name = "LockID"
#    type = "S"
#  }
#  
#  tags = {
#    ManagedBy = "terraform"
#  }
#}

# S3 bucket for Terraform state
#resource "aws_s3_bucket" "terraform_state" {
#  bucket = "veloscope-terraform-state"
#  
#  tags = {
#    Name = "Veloscope Terraform State"
#    ManagedBy = "terraform"
#  }
#  
#  lifecycle {
#    prevent_destroy = true
#  }
#}
#
#resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
#  bucket = aws_s3_bucket.terraform_state.id
#  
#  versioning_configuration {
#    status = "Enabled"
#  }
#}
