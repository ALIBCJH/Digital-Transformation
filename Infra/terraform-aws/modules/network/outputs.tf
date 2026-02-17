#purpose: exports the vpc vpc_id and the subnets_ids so that the Database and compute modules know where to build the resources
output "vpc_id" {
  value = aws_vpc.main.id
}
output "public_subnets_id" {
  value = aws_subnet.public_1.id
}


