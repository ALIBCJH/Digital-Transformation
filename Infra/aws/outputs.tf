output "ssh_command" {
  description = "SSH command to connect to EC2"
  value       = "ssh -i juma-key.pem ubuntu@${aws_instance.web.public_ip}"
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
  description = "RDS database endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_hostname" {
    description = "RDS instance hostname"
    value       = aws_db_instance.postgres.endpoint
}

output "rds_port" {
    description = "RDS instance port"
    value = aws_db_instance.postgres.port
}

output "rds_username" {
    description = "RDS instance root username"
    value = aws_db_instance.postgres.username
}
