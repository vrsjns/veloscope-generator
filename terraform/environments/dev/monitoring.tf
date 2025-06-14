module "monitoring" {
  source = "../../modules/monitoring"

  environment      = var.environment
  aws_region       = var.aws_region
  cluster_name     = module.ecs.cluster_name
  cpu_threshold    = 80
  memory_threshold = 80
  alert_email      = var.alert_email
}