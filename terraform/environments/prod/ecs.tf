module "ecs" {
  source = "../../modules/ecs"

  environment               = var.environment
  aws_region                = var.aws_region
  vpc_id                    = data.terraform_remote_state.shared.outputs.vpc_id
  enable_container_insights = true  # Enable for production for better monitoring

  # Task resources - more resources for production
  prepare_batch_cpu       = "512"
  prepare_batch_memory    = "1024"
  upload_batch_cpu        = "512"
  upload_batch_memory     = "1024"
  download_batch_cpu      = "512"
  download_batch_memory   = "1024"

  # Roles
  execution_role_arn = module.iam.batch_role_arn
  task_role_arn      = module.iam.batch_role_arn

  # Image URLs
  prepare_batch_image_url  = data.terraform_remote_state.shared.outputs.ecr_prepare_batch_repository_url
  upload_batch_image_url   = data.terraform_remote_state.shared.outputs.ecr_upload_batch_repository_url
  download_batch_image_url = data.terraform_remote_state.shared.outputs.ecr_download_batch_repository_url

  # Other resources
  s3_bucket_id            = module.storage.bucket_id
  openai_api_key_arn      = aws_ssm_parameter.openai_api_key.arn
  log_group_name          = aws_cloudwatch_log_group.batch_logs.name
}
