module "iam" {
  source = "../../modules/iam"

  environment         = var.environment
  s3_bucket_arn       = module.storage.bucket_arn
  openai_api_key_arn  = aws_ssm_parameter.openai_api_key.arn
  log_group_arn       = aws_cloudwatch_log_group.batch_logs.arn
  cluster_arn         = module.ecs.cluster_arn
  task_definition_arns = [
    module.ecs.prepare_batch_task_definition_arn,
    module.ecs.upload_batch_task_definition_arn,
    module.ecs.download_batch_task_definition_arn
  ]
}