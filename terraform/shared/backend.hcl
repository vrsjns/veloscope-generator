bucket         = "veloscope-terraform-state"
key            = "veloscope/shared/terraform.tfstate"
region         = "eu-central-1"
encrypt        = true
dynamodb_table = "veloscope-terraform-locks"
