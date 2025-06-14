# Public subnets for the environment
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = var.vpc_id
  cidr_block              = var.environment == "production" ? "10.0.1.0/24" : "10.0.101.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name        = "veloscope-${var.environment}-public-subnet-1"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = var.vpc_id
  cidr_block              = var.environment == "production" ? "10.0.2.0/24" : "10.0.102.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name        = "veloscope-${var.environment}-public-subnet-2"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Route table for public subnets
resource "aws_route_table" "public_rt" {
  vpc_id = var.vpc_id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = data.aws_internet_gateway.igw.id
  }

  tags = {
    Name        = "veloscope-${var.environment}-public-rt"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Find the Internet Gateway
data "aws_internet_gateway" "igw" {
  filter {
    name   = "attachment.vpc-id"
    values = [var.vpc_id]
  }
}

# Associate route table with public subnets
resource "aws_route_table_association" "public_rta_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_rta_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.public_rt.id
}

# Security group for ECS tasks
resource "aws_security_group" "ecs_sg" {
  name        = "veloscope-${var.environment}-ecs-sg"
  description = "Security group for Veloscope ECS tasks"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "veloscope-${var.environment}-ecs-sg"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Get the VPC details
data "aws_vpc" "selected" {
  id = var.vpc_id
}

# Get the available subnets in the VPC
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "map-public-ip-on-launch"
    values = ["true"]
  }
}

# Output values
output "security_group_id" {
  description = "ID of the security group for ECS tasks"
  value       = aws_security_group.ecs_sg.id
}

output "subnet_ids" {
  description = "IDs of the public subnets"
  value       = data.aws_subnets.public.ids
}