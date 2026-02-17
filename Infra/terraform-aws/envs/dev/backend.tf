terraform {
  backend "s3" {
    bucket         = "chuo-market"
    key            = "dev/terraform.tfstate"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "terraform-lock-table"
  }
}
