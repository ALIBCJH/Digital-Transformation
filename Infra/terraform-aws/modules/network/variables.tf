variable "vpc_cidr" {
    description = "CIDR Block for the VPC"
    type = string
    default = "10.0.0.0/16"
}
variable "public_subnet_cidr" {
    description = "lists of the public subnets"
    type = list(string)
}
variable "private_subnet_cidr" {
    description = "CIDR block for private subnets"
    type = list(string)
}
variable "aws_internet_gateway" {
    description = "Boolean to create internet gateway"
    type = bool
    default = true
}
