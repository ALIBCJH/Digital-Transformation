#PURPOSE: This file calls the modules from the module
#directory to create the required resources in the dev environment

module "network" {
  source = "../../modules/network"
  
  # Network configuration parameters

  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidr   = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidr  = ["10.0.3.0/24", "10.0.4.0/24"]
}

module "compute" {
  source = "../../modules/compute"
  
  # Pass VPC information from network module outputs to compute module
  vpc_id    = module.network.vpc_id
  subnet_id = module.network.public_subnet[0]
  
  # Compute-specific configuration
  instance_type   = "t2.micro"
  cpu             = 256
  memory          = 512
  container_image = ""
}