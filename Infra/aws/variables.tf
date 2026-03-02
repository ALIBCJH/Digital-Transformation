variable "aws_region" {
    default = "us-east-1"
}
variable "db_username" {
    default = "admin"
    type = string
}
variable "db_password" {
    default = "database password"
    type = string
    sensitive = true
}
variable "db_name" {
    default = "mydatabase"
    type = string
}
variable "vpc_id" {
    default = "vpc_example"
    type = string
}
variable "key_name"{
    default = "my_key_pair"
    type = string
}