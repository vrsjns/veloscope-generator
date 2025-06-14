module "scheduling" {
  source = "../../modules/scheduling"

  environment                        = var.environment
  cluster_arn                        = module.ecs.cluster_arn
  events_role_arn                    = module.iam.events_role_arn
  prepare_batch_task_definition_arn  = module.ecs.prepare_batch_task_definition_arn
  upload_batch_task_definition_arn   = module.ecs.upload_batch_task_definition_arn
  download_batch_task_definition_arn = module.ecs.download_batch_task_definition_arn
  subnet_ids                         = module.networking.subnet_ids
  security_group_id                  = module.networking.security_group_id
  
  # Development-specific schedule expressions
  prepare_batch_schedule_expression  = "cron(5 1 * * ? *)"   # 1:05 AM UTC daily
  upload_batch_schedule_expression   = "cron(15 1 * * ? *)"  # 1:15 AM UTC daily
  download_batch_schedule_expression = "cron(30 * * * ? *)"  # 30 minutes past every hour
}