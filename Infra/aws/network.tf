resource "aws_security_group" "rds_sg" {
    name   = "postgres-rds-sg"
    # This links directly to the VPC in main.tf
    vpc_id = aws_vpc.main.id 

    ingress {
        from_port   = 5432
        to_port     = 5432
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}