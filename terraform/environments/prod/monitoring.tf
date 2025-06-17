module "monitoring" {
  source = "../../modules/monitoring"

  environment      = var.environment
  aws_region       = var.aws_region
  cluster_name     = module.ecs.cluster_name
  cpu_threshold    = 70  # More sensitive threshold for production
  memory_threshold = 70  # More sensitive threshold for production
  alert_email      = var.alert_email
}
