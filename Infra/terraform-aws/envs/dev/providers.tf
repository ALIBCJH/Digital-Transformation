#Providers are plugins that connect terraform with AWS 

provider "aws" {
  region = var.aws_region
}
