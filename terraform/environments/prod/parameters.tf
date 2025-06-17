# SSM Parameter for OpenAI API key
resource "aws_ssm_parameter" "openai_api_key" {
  name        = "/veloscope/${var.environment}/openai-api-key"
  description = "OpenAI API key for Veloscope"
  type        = "SecureString"
  value       = var.openai_api_key

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
