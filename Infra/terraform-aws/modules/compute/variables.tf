
variable "subnet_id" {
  type = list(string)
}
variable "cpu" {
  type = number
}
variable "memory" {
  type = number
}
variable "container_image" {
  type = string
}
variable "instance_type" {
  type = string
  description = "EC2 instace type for compute resources"
}
variable "vpc_id" {
  type = string
  description = "VPC ID where compute resouces will be deployed"
}