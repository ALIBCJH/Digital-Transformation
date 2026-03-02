# Frontend + Backend Deployment on AWS EC2

## Overview

This setup deploys both React frontend and Django backend on a single AWS EC2 instance using Docker containers. The architecture uses:

- **Frontend**: React app served by Nginx (Port 80)
- **Backend**: Django API (Port 8000)
- **Database**: AWS RDS PostgreSQL (Private subnet)
- **Networking**: VPC with public subnets, Internet Gateway
- **Security**: Security groups restricting access appropriately

## Architecture

```
                    ┌─────────────────┐
                    │   Internet      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Internet GW    │
                    └────────┬────────┘
                             │
         ┌───────────────────┴──────────────────┐
         │                                       │
┌────────▼────────┐                   ┌─────────▼────────┐
│  Port 80 (HTTP) │                   │  Port 8000 (API) │
│  Port 443(HTTPS)│                   └──────────────────┘
└────────┬────────┘                             
         │                                       
    ┌────▼─────────────────────┐                
    │    EC2 Instance          │                
    │    (t3.small)            │                
    │  ┌──────────────┐        │                
    │  │  Frontend    │        │                
    │  │  Container   │───┐    │                
    │  │  (Nginx)     │   │    │                
    │  └──────────────┘   │    │                
    │         │            │    │                
    │         │ /api/*     │    │                
    │         │            │    │                
    │  ┌──────▼──────┐    │    │                
    │  │  Backend    │◄───┘    │                
    │  │  Container  │         │                
    │  │  (Django)   │         │                
    │  └──────┬──────┘         │                
    └─────────┼────────────────┘                
              │                                  
              │ Database Connection              
              │ (Private VPC)                    
     ┌────────▼────────┐                         
     │   AWS RDS       │                         
     │   PostgreSQL    │                         
     │  (Private)      │                         
     └─────────────────┘                         
```

## Infrastructure Resources (Terraform)

### Networking
- **VPC**: 10.0.0.0/16
- **Public Subnets**: 
  - 10.0.1.0/24 (eu-north-1a)
  - 10.0.2.0/24 (eu-north-1b)
- **Internet Gateway**: For public access
- **Route Tables**: Routes internet traffic through IGW

### Compute
- **EC2 Instance**: t3.small (2 vCPU, 2GB RAM)
  - Runs both frontend and backend containers
  - Docker and Docker Compose pre-installed
  - SSM agent for secure deployments
  - Automatic network creation for container communication

### Database
- **RDS PostgreSQL**: db.t3.micro
  - Engine version: 16
  - Storage: 20GB
  - **Private** - not publicly accessible
  - Accessible only from EC2 instance in same VPC

### Security Groups
- **Port 22** (SSH): Restricted to your IP only
- **Port 80** (HTTP): Open to internet (frontend)
- **Port 443** (HTTPS): Open to internet (future SSL)
- **Port 8000** (Backend API): Open to internet
- **Port 5432** (PostgreSQL): Only from VPC (10.0.0.0/16)

## Deployment Pipeline

The CI/CD pipeline consists of 4 jobs:

### 1. Terraform Infrastructure
- Provisions/updates AWS infrastructure
- Only applies changes on `main` branch
- Shows plan preview on Pull Requests
- Outputs EC2 instance ID for deployment

### 2. Test & Lint
- Runs Python linting (Ruff)
- Security audits (Safety, Bandit)
- Django test suite
- Runs in parallel with Terraform

### 3. Build & Push Docker Images
- Builds **backend** Docker image
- Builds **frontend** Docker image
- Pushes both to GitHub Container Registry (GHCR)
- Uses Docker BuildKit caching for faster builds
- Tags: `main`, `sha-xxxxx`, `latest`

### 4. Deploy to AWS EC2
- Only runs on `main` branch
- Uses AWS SSM (no SSH keys needed)
- Deploys using Docker Compose
- Zero-downtime deployment:
  1. Pull new images
  2. Stop old containers
  3. Start new containers
  4. Clean up old images

## Environment Variables

### GitHub Secrets Required

#### AWS & Infrastructure
- `AWS_ROLE_ARN` - IAM role ARN for OIDC authentication
- `TF_STATE_BUCKET` - S3 bucket for Terraform state
- `DB_PASSWORD` - PostgreSQL password for RDS

#### Application
- `DJANGO_SECRET_KEY` - Django secret key
- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_HOSTS` - Django allowed hosts (EC2 IP or domain)
- `EC2_INSTANCE_ID` - (Optional) Fallback EC2 instance ID

## Frontend Configuration

### Nginx Proxy
The frontend Nginx container proxies API requests to the backend:

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    # Proper headers for proxy
}
```

### API Configuration
Frontend uses relative URLs in production:
- Development: `http://127.0.0.1:8000/api`
- Production: `/api` (proxied by Nginx to backend container)

### Environment Variables (Frontend)
- `VITE_API_BASE_URL=/api` - Set during production build

## Docker Compose Setup

The production deployment uses `docker-compose.prod.yml`:

```yaml
services:
  backend:
    image: ghcr.io/user/backend:sha-xxx
    ports: ["8000:8000"]
    environment:
      - SECRET_KEY=...
      - DATABASE_URL=...
    networks: [app-network]
    
  frontend:
    image: ghcr.io/user/frontend:sha-xxx
    ports: ["80:80"]
    depends_on: [backend]
    networks: [app-network]
```

## Container Communication

Containers communicate via a shared Docker network (`app-network`):

1. **Frontend ↔ Backend**: Nginx proxies `/api/*` to `http://backend:8000`
2. **Backend ↔ Database**: Direct connection via DATABASE_URL
3. **User ↔ Frontend**: HTTP on port 80
4. **User ↔ Backend**: Direct access on port 8000 (optional)

## Cost Optimization

### Instance Sizing
- **t3.small** ($0.016/hour ~$12/month): Sufficient for both containers
- **Alternative**: t3.micro for very low traffic (but may struggle)
- **Scale up**: t3.medium for production with high traffic

### Database
- **db.t3.micro** ($0.016/hour ~$12/month): Free tier eligible
- **Alternative**: Aurora Serverless for variable workloads

### Total Monthly Cost (estimate)
- EC2 (t3.small): ~$12
- RDS (db.t3.micro): ~$12
- Data Transfer: ~$1-5
- S3 (State): <$1
- **Total**: ~$25-30/month

## Scaling Considerations

### Vertical Scaling (Same EC2)
- Upgrade to t3.medium (4GB RAM)
- Upgrade to t3.large (8GB RAM)

### Horizontal Scaling (Multiple Instances)
1. Add Application Load Balancer
2. Deploy frontend/backend to multiple EC2 instances
3. Use RDS read replicas for database scaling
4. Consider moving frontend to S3 + CloudFront

### Container Scaling
```yaml
services:
  backend:
    deploy:
      replicas: 3  # Run 3 backend containers
```

## Security Best Practices

✅ **Implemented:**
- OIDC authentication (no long-lived AWS credentials)
- SSH restricted to your IP
- Database in private subnet
- HTTPS-ready security group rules
- Encrypted S3 state storage
- Container healthchecks

🔒 **Recommended Next Steps:**
- Set up SSL/TLS with Let's Encrypt
- Use AWS Secrets Manager for sensitive data
- Enable CloudWatch monitoring
- Set up automated backups for RDS
- Implement Web Application Firewall (WAF)
- Use Route53 for custom domain

## Monitoring & Logging

### Container Logs
```bash
# SSH into EC2
ssh -i juma-key.pem ubuntu@<ec2-ip>

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check container status
docker ps
docker stats
```

### AWS CloudWatch
- EC2 metrics (CPU, memory, disk)
- RDS metrics (connections, queries)
- Set up alarms for high resource usage

### Application Monitoring
- Add Django logging configuration
- Use Sentry for error tracking
- Consider AWS X-Ray for distributed tracing

## Backup & Recovery

### Database Backups
- RDS automated daily backups (7-day retention)
- Manual snapshots before major changes

### Infrastructure Recovery
```bash
# Terraform can recreate everything
cd Infra/aws
terraform destroy  # Remove old infrastructure
terraform apply    # Recreate infrastructure
```

### Application Recovery
```bash
# Redeploy via GitHub Actions
git commit --allow-empty -m "Trigger redeploy"
git push origin main
```

## Troubleshooting

### Container Not Starting
```bash
docker logs backend
docker logs frontend
docker inspect backend
```

### Network Issues
```bash
docker network ls
docker network inspect app-network
ping backend  # From within frontend container
```

### Database Connection Issues
```bash
# Check security group rules
# Verify DATABASE_URL is correct
# Test connection from EC2:
psql $DATABASE_URL
```

### Deployment Failures
```bash
# Check SSM command status
aws ssm list-commands --instance-id i-xxxxx
aws ssm get-command-invocation --command-id cmd-xxx --instance-id i-xxx
```

## Manual Deployment (If CI/CD Unavailable)

```bash
# 1. SSH into EC2
ssh -i juma-key.pem ubuntu@<ec2-ip>

# 2. Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin

# 3. Create/update docker-compose.yml
# 4. Set environment variables
export BACKEND_IMAGE=ghcr.io/user/backend:latest
export FRONTEND_IMAGE=ghcr.io/user/frontend:latest
export DJANGO_SECRET_KEY="..."
export DATABASE_URL="..."
export ALLOWED_HOSTS="..."

# 5. Deploy
docker-compose pull
docker-compose down
docker-compose up -d

# 6. Verify
docker ps
curl http://localhost
curl http://localhost:8000/api/health/
```

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Frontend URL | http://localhost:5173 | http://<ec2-ip> |
| Backend URL | http://localhost:8000 | http://<ec2-ip>:8000 |
| API Base URL | http://127.0.0.1:8000/api | /api (proxied) |
| Database | SQLite or local Postgres | AWS RDS |
| SSL | No | Recommended |
| Deployment | Manual | Automated CI/CD |

## Next Steps

1. ✅ Set up S3 backend for Terraform state
2. ✅ Configure GitHub secrets
3. ✅ Run `terraform init` locally first
4. ✅ Create a feature branch and test the pipeline
5. ✅ Merge to main to deploy
6. 🔲 Add custom domain name
7. 🔲 Configure SSL certificate
8. 🔲 Set up CloudWatch alarms
9. 🔲 Enable automated RDS backups
10. 🔲 Add monitoring and logging solution

## Support

For issues or questions:
- Check GitHub Actions logs
- Review Terraform plan output
- Inspect container logs via SSH
- Check AWS CloudWatch for infrastructure metrics
