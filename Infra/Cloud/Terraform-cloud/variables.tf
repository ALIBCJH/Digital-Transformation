#This file contains the variables used in the terraform configs for deploying resources
# to digitalOcean it includes the digital ocean API token
# and the region to deploy the resources in

variable "do_token" {
    type = string
    description = "DigitalOcean API token"
    sensitive =  true
}
variable "region" {
    type = string
    description = "Available DigitalOcean region"
    default = "nyc3"
}
variable "ssh_key_name" {
    type = string
    description = "Name of the SSH key aas it appears in DigitalOcean"
}