# Terraform Backend Configuration for S3
# This stores your Terraform state in S3 (recommended for production)
# The actual values are passed via -backend-config flags in CI/CD

terraform {
  backend "s3" {
    # These will be provided via GitHub Actions:
    # bucket = "your-terraform-state-bucket"
    # key    = "production/terraform.tfstate"
    # region = "eu-north-1"
    
    encrypt        = true
    dynamodb_table = "terraform-state-lock"  # For state locking (optional but recommended)
  }
}
