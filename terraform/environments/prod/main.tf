terraform {
  backend "s3" {} # Empty configuration to be filled by -backend-config
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

# Reference shared infrastructure
data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket  = "veloscope-terraform-state"
    key     = "veloscope/shared/terraform.tfstate"
    region  = var.aws_region
    profile = var.aws_profile
  }
}

# Set up networking for this environment
module "networking" {
  source = "../../modules/networking"

  vpc_id      = data.terraform_remote_state.shared.outputs.vpc_id
  environment = var.environment
  aws_region  = var.aws_region
}

# Set up storage for this environment
module "storage" {
  source = "../../modules/storage"

  environment = var.environment
  bucket_name = var.s3_bucket_name
}