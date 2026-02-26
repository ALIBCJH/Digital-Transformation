provider "aws" {
  region = "eu-north-1" # Stockholm
}

# --- AUTOMATED SSH KEY GENERATION ---
resource "tls_private_key" "main_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "aws_key_pair" "generated_key" {
  key_name   = "juma-stockholm-key-v2" # Incremented version
  public_key = tls_private_key.main_key.public_key_openssh
}

resource "local_file" "ssh_key_file" {
  content         = tls_private_key.main_key.private_key_pem
  filename        = "juma-key.pem"
  file_permission = "0400"
}

# --- NETWORK SETUP ---
#----Setting Up the whole network infra, the big network
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16" # The big network
  enable_dns_hostnames = true 
  tags = { Name = "juma-vpc" }
}

resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "juma-gateway" }
}

#This tells traffic where to go
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0" # This is the internet gateway that allows traffic from the vpc to the outside world
    gateway_id = aws_internet_gateway.gw.id
  }
}

//Allows specific resources in this subnet to receive traffic from the internet, ie an ec2 instance running django backend
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

# --- RDS SUBNET GROUP (FIXED NAME) ---
resource "aws_db_subnet_group" "db_subnets" {
  name       = "juma-db-subnet-group-v2" # V2 to avoid VPC conflict
  subnet_ids = [aws_subnet.public.id, aws_subnet.public_b.id]
}

# --- SECURITY ---
resource "aws_security_group" "allow_ssh_pg" {
  name        = "allow_ssh_and_postgres_v2" # V2 to ensure it attaches to new VPC
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22 # Allow inbound connection to reach our endpoints
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 5432 # Allows every resources configured in our cloud infra to reach the internet
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- COMPUTE (EC2) ---
resource "aws_instance" "web" {
  ami                    = "ami-08eb150f611ca277f" 
  instance_type          = "t3.micro" 
  key_name               = aws_key_pair.generated_key.key_name
  vpc_security_group_ids = [aws_security_group.allow_ssh_pg.id]
  subnet_id              = aws_subnet.public.id

  tags = { Name = "Juma-Dev-Server" }
}

# --- DATABASE (RDS) ---
resource "aws_db_instance" "postgres" {
  allocated_storage      = 20
  engine                 = "postgres"
  engine_version         = "16" 
  instance_class         = "db.t3.micro"
  db_name                = "myappdb"
  username               = "simonadmin"
  password               = "YourSecurePassword123!" 
  db_subnet_group_name   = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids = [aws_security_group.allow_ssh_pg.id]
  publicly_accessible    = true
  skip_final_snapshot    = true
}

# --- OUTPUTS ---
output "ssh_command" {
  value = "ssh -i juma-key.pem ubuntu@${aws_instance.web.public_ip}"
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}