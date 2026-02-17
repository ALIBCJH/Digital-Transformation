#Declares the name of the variables specific to the development environment

variable "aws_region" {
  description = "aws region "
  type        = string
  default     = "eu-north-1"
}
variable "vpc_cidr" {
  description = "CIDR blocks for vpc"
  type =  string
  default = "10.0.0.0/16"
}
variable "public_subnet_cidrs" {
  description = "CIDR block for public subnets"
  type = list(string)
  default = ["10.0.3.0/24", "10.0.4.0/24"]
}
variable "vpc_id" {
  type = string

}
variable "subnet_id" {
  type = list(string)
}
variable "instance_type" {
  type = string
}
variable "cpu" {
  type = number
}
variable "vpc_id" {
  type = string
}

