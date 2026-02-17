#This file locks the version of Terraform and the provider
#prevents the idea that it works on my machine bug

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"

    }
  }
}
