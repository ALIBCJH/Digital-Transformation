terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }

  backend "s3" {
    bucket         = "juma-terraform-state-storage-2026"
    key            = "digital-transformation/terraform.tfstate"
    region         = "eu-north-1"
    dynamodb_table = "terraform-state-locking"
    encrypt        = true
  }
}

provider "aws" {
  region = "eu-north-1"  # Keep eu-north-1 since your resources are already there
}