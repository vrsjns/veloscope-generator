# Veloscope Terraform Infrastructure

This directory contains the Terraform configurations for the Veloscope project.

## Structure
- `shared/`: Contains shared infrastructure resources used across all environments
  - `backend.hcl`: Backend configuration for shared infrastructure
  - `terraform.tfvars`: Variables for shared infrastructure
- `modules/`: Reusable Terraform modules
- `environments/`: Environment-specific configurations
  - `dev/`: Development environment
    - `backend.hcl`: Backend configuration for dev environment
    - `terraform.tfvars`: Variables for dev environment
  - `prod/`: Production environment
    - `backend.hcl`: Backend configuration for prod environment
    - `terraform.tfvars`: Variables for prod environment

## Usage
0. Prepare AWS for Terraform state storage (one-time setup):
    ```bash
    # Create S3 bucket for Terraform state
    aws s3 mb s3://veloscope-terraform-state --region [YOUR_AWS_REGION]

    # Enable versioning on the S3 bucket
    aws s3api put-bucket-versioning --bucket veloscope-terraform-state --versioning-configuration Status=Enabled

    # Create DynamoDB table for state locking
    aws dynamodb create-table \
      --table-name veloscope-terraform-locks \
      --attribute-definitions AttributeName=LockID,AttributeType=S \
      --key-schema AttributeName=LockID,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST \
      --region [YOUR_AWS_REGION]
    ```

1. Apply shared infrastructure first:
    ```bash
    cd shared
    terraform init -backend-config=backend.hcl
    terraform apply -var-file=terraform.tfvars
    ```

2. Apply environment-specific infrastructure:
    ```bash
    cd environments/{prod|dev}
    terraform init -backend-config=backend.hcl
    terraform apply -var-file=terraform.tfvars
    ```

## Important Notes
- Always apply shared infrastructure before environment-specific resources
- Use appropriate AWS credentials for each environment
- Review changes carefully before applying, especially in production
