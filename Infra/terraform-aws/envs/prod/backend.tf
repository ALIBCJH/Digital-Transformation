#configures remote state 

terraform {
  backend "s3" {
    bucket         = ""
    key            = "prod/terraform.tfstate"                 # Different path!
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}
