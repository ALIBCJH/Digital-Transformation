provider "aws" {
  region = "eu-north-1" # Stockholm
}

# --- FETCH YOUR CURRENT IP ADDRESS ---
data "http" "my_ip" {
  url = "http://ipv4.icanhazip.com"
}

# --- AUTOMATED SSH KEY GENERATION ---
resource "tls_private_key" "main_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "juma-stockholm-key-v3"
  public_key = tls_private_key.main_key.public_key_openssh
}

resource "local_file" "ssh_key_file" {
  content         = tls_private_key.main_key.private_key_pem
  filename        = "juma-key.pem"
  file_permission = "0400"
}

# --- NETWORK SETUP ---
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "juma-vpc" }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "juma-gateway" }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "eu-north-1a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "public_b" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "eu-north-1b"
  map_public_ip_on_launch = true
}

resource "aws_route_table_association" "a" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "b" {
  subnet_id      = aws_subnet.public_b.id
  route_table_id = aws_route_table.public_rt.id
}

# --- RDS SUBNET GROUP ---
resource "aws_db_subnet_group" "db_subnets" {
  name       = "juma-db-subnet-group-v3"
  subnet_ids = [aws_subnet.public.id, aws_subnet.public_b.id]
}

# --- SECURITY GROUPS ---
resource "aws_security_group" "allow_ssh_pg" {
  name   = "allow_ssh_and_postgres_v3"
  vpc_id = aws_vpc.main.id

  # 1. SSH Access: Only allowed from your detected IP
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${chomp(data.http.my_ip.response_body)}/32"]
  }

  # 2. HTTP Access: Public access for frontend
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 3. HTTPS Access: Public access for frontend (SSL)
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 4. Backend API: Public access for API endpoints
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 5. Database Access: Only allowed from within the VPC network
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block] # 10.0.0.0/16
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "juma-web-security-group" }
}

# --- COMPUTE (EC2) ---
resource "aws_instance" "web" {
  ami                    = "ami-08eb150f611ca277f"
  instance_type          = "t3.small" # Upgraded for running both frontend and backend
  key_name               = aws_key_pair.generated_key.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh_pg.id]
  subnet_id              = aws_subnet.public.id

  # User data script to install Docker and Docker Compose
  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # Update system
              apt-get update
              apt-get upgrade -y
              
              # Install Docker
              curl -fsSL https://get.docker.com -o get-docker.sh
              sh get-docker.sh
              usermod -aG docker ubuntu
              
              # Install Docker Compose
              curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
              chmod +x /usr/local/bin/docker-compose
              
              # Install SSM agent (if not present)
              snap install amazon-ssm-agent --classic
              systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
              systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service
              
              # Create docker network for frontend-backend communication
              docker network create app-network || true
              
              echo "Setup complete" > /var/log/user-data-complete.log
              EOF

  tags = { Name = "Juma-Production-Server" }
}

# --- DATABASE (RDS) ---
resource "aws_db_instance" "postgres" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = "db.t3.micro"
  db_name                = "myappdb"
  username               = "simonadmin"
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids = [aws_security_group.allow_ssh_pg.id]
  
  # --- PROTECTED FROM INTERNET ---
  publicly_accessible    = false 
  skip_final_snapshot    = true
}

# --- OUTPUTS ---
output "ssh_command" {
  value = "ssh -i juma-key.pem ubuntu@${aws_instance.web.public_ip}"
}

output "ec2_instance_id" {
  description = "EC2 Instance ID for deployment"
  value       = aws_instance.web.id
}

output "ec2_public_ip" {
  description = "Public IP of EC2 instance"
  value       = aws_instance.web.public_ip
}

output "frontend_url" {
  description = "Frontend application URL"
  value       = "http://${aws_instance.web.public_ip}"
}

output "backend_url" {
  description = "Backend API URL"
  value       = "http://${aws_instance.web.public_ip}:8000"
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}