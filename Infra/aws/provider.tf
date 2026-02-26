terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = ">= 5.0"
        }
    }
#      backend "s3" {
#     bucket = "myapp_terraform_state_bucket"
#     key = "rds/terraform.tf.state"
#     region = var.aws_region
#     dynamodb_table = "terraform-state-locking"
#     encrypt = true
#  } 
}
  




