bucket         = "veloscope-terraform-state"
key            = "veloscope/production/terraform.tfstate"
region         = "[YOUR_AWS_REGION]"
encrypt        = true
dynamodb_table = "veloscope-terraform-locks"
