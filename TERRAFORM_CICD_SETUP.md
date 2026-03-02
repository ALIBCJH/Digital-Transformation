# Infrastructure as Code CI/CD Pipeline Setup Guide

This guide explains how to set up automated Terraform infrastructure provisioning in your GitHub Actions CI/CD pipeline.

## 🎯 Overview

The new workflow automates:
1. **Terraform**: Provisions AWS infrastructure (VPC, EC2, RDS, Security Groups)
2. **Testing**: Runs Django tests and security checks
3. **Docker Build**: Builds and pushes Docker image to GHCR
4. **Deployment**: Deploys application to provisioned EC2 instance

## 📋 Prerequisites

Before setting up the pipeline, you need:

### 1. AWS S3 Bucket for Terraform State

Create an S3 bucket to store Terraform state:

```bash
# Create S3 bucket for state storage
aws s3 mb s3://your-company-terraform-state --region eu-north-1

# Enable versioning (important for state recovery)
aws s3api put-bucket-versioning \
  --bucket your-company-terraform-state \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket your-company-terraform-state \
  --server-side-encryption-configuration '{
    "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]
  }'

# Block public access
aws s3api put-public-access-block \
  --bucket your-company-terraform-state \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

### 2. DynamoDB Table for State Locking (Optional but Recommended)

Prevents concurrent Terraform runs from corrupting state:

```bash
aws dynamodb create-table \
  --table-name terraform-state-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region eu-north-1
```

### 3. AWS IAM Role for GitHub Actions (OIDC)

You already have this configured! Your existing `AWS_ROLE_ARN` needs additional Terraform permissions:

**Required IAM Policy** (add to your existing role):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformStateAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-company-terraform-state",
        "arn:aws:s3:::your-company-terraform-state/*"
      ]
    },
    {
      "Sid": "TerraformStateLocking",
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:GetItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:eu-north-1:*:table/terraform-state-lock"
    },
    {
      "Sid": "TerraformResourceManagement",
      "Effect": "Allow",
      "Action": [
        "ec2:*",
        "rds:*",
        "vpc:*",
        "elasticloadbalancing:*"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🔐 GitHub Secrets Required

Add these secrets to your GitHub repository (`Settings` → `Secrets and variables` → `Actions`):

### Existing Secrets (you should already have these):
- ✅ `AWS_ROLE_ARN` - Your AWS IAM role ARN for OIDC
- ✅ `DJANGO_SECRET_KEY` - Django secret key
- ✅ `DATABASE_URL` - Database connection string
- ✅ `ALLOWED_HOSTS` - Django allowed hosts
- ✅ `EC2_INSTANCE_ID` - (Optional fallback if Terraform doesn't output it)

### New Secrets Required:
- `TF_STATE_BUCKET` - S3 bucket name for Terraform state (e.g., `your-company-terraform-state`)
- `DB_PASSWORD` - PostgreSQL password for RDS (used by Terraform)

## 🚀 Workflow Behavior

### On Pull Requests:
1. **Terraform Plan** - Shows what infrastructure changes would be made
2. **Test & Lint** - Validates application code
3. **Docker Build** - Builds image but tests it
4. ❌ **No Apply** - Infrastructure is NOT changed
5. ❌ **No Deploy** - Application is NOT deployed

### On Push to `main` Branch:
1. ✅ **Terraform Apply** - Provisions/updates infrastructure
2. ✅ **Test & Lint** - Validates code
3. ✅ **Docker Build & Push** - Pushes to GHCR
4. ✅ **Deploy to AWS** - Deploys to EC2

### On Push to `develop` Branch:
1. ✅ **Terraform Plan** - Shows changes
2. ✅ **Test & Lint** - Validates code  
3. ✅ **Docker Build & Push** - Pushes to GHCR
4. ❌ **No Deploy** - Only main branch deploys

## 📁 File Structure

```
.github/workflows/
├── infrastructure-and-deploy.yml   # NEW: Complete automation pipeline
├── django-ci.yml                   # OLD: Can be deprecated
└── deploy.yml                      # DEPRECATED

Infra/aws/
├── main.tf                         # Infrastructure resources
├── backend.tf                      # NEW: S3 backend configuration
├── variables.tf                    # Input variables
└── outputs.tf                      # Output values (optional)
```

## 🎬 Getting Started

### Step 1: Create S3 Bucket & DynamoDB Table
```bash
# Run the commands from Prerequisites section above
```

### Step 2: Update IAM Role Permissions
```bash
# Attach the Terraform IAM policy to your GitHub Actions role
aws iam put-role-policy \
  --role-name GitHubActionsRole \
  --policy-name TerraformAccess \
  --policy-document file://terraform-policy.json
```

### Step 3: Add GitHub Secrets
```bash
# In GitHub: Settings → Secrets and variables → Actions
# Add: TF_STATE_BUCKET and DB_PASSWORD
```

### Step 4: Initialize Terraform Backend (Local First)
```bash
cd Infra/aws

# Initialize with S3 backend
terraform init \
  -backend-config="bucket=your-company-terraform-state" \
  -backend-config="key=production/terraform.tfstate" \
  -backend-config="region=eu-north-1"

# Verify plan works
terraform plan -var="db_password=YourSecurePassword"
```

### Step 5: Test the Workflow
```bash
# Create a feature branch
git checkout -b feature/test-terraform-cicd

# Make a small change
echo "# Test" >> README.md

# Commit and push
git add README.md
git commit -m "Test Terraform CI/CD pipeline"
git push origin feature/test-terraform-cicd

# Create a PR and check the Terraform plan in the PR comments
```

### Step 6: Deploy to Production
```bash
# Merge to main branch
git checkout main
git merge feature/test-terraform-cicd
git push origin main

# Watch the GitHub Actions workflow provision infrastructure and deploy!
```

## 🎯 Best Practices Implemented

### ✅ Security
- OIDC authentication (no long-lived credentials)
- Encrypted state storage in S3
- State locking with DynamoDB
- Sensitive outputs marked appropriately

### ✅ GitOps Workflow
- Infrastructure changes via Pull Requests
- Plan preview in PR comments
- Only `main` branch can apply changes
- Full audit trail in Git history

### ✅ Deployment Safety
- Tests run before deployment
- Infrastructure provisioned before deployment
- Rollback capability via Git revert
- Deployment only on successful builds

### ✅ Environment Separation
- `main` → Production (auto-deploy)
- `develop` → Staging (build only)
- Feature branches → Testing (plan only)

## 🔧 Customization Options

### Multiple Environments

To support dev/staging/prod, you can:

1. **Use Terraform Workspaces**:
```yaml
- name: Select Workspace
  run: |
    terraform workspace select ${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}
```

2. **Use Different State Keys**:
```yaml
- name: Terraform Init
  run: |
    terraform init \
      -backend-config="key=${{ github.ref == 'refs/heads/main' && 'prod' || 'dev' }}/terraform.tfstate"
```

### Manual Approval for Production

Add environment protection rules:

```yaml
deploy-to-aws:
  environment:
    name: production
    url: https://your-app.com
  # In GitHub: Settings → Environments → production → Required reviewers
```

### Drift Detection

Add a scheduled workflow to detect infrastructure drift:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
```

## 📊 Monitoring & Debugging

### View Terraform Plan
- PR comments show the plan automatically
- Check Actions tab for detailed logs

### Check Terraform State
```bash
# List resources in state
terraform state list

# Show specific resource
terraform state show aws_instance.web
```

### Debug Deployment Issues
```bash
# Check SSM command status
aws ssm list-commands --instance-id i-xxxxx

# View command output
aws ssm get-command-invocation --command-id cmd-xxxxx --instance-id i-xxxxx
```

## 🚨 Troubleshooting

### "Error: Backend initialization required"
```bash
# Re-initialize backend locally
terraform init -reconfigure
```

### "Error: State lock already held"
```bash
# Check DynamoDB for stuck locks
aws dynamodb scan --table-name terraform-state-lock

# Force unlock (use with caution!)
terraform force-unlock <LOCK_ID>
```

### "Error: Insufficient IAM permissions"
```bash
# Check CloudTrail for denied actions
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=AccessDenied
```

## 📚 Additional Resources

- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions with OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

## 🎉 Next Steps

1. ✅ Create S3 bucket and DynamoDB table
2. ✅ Update IAM role permissions
3. ✅ Add GitHub secrets
4. ✅ Initialize Terraform backend
5. ✅ Test on feature branch
6. ✅ Deploy to production
7. 🔄 Monitor and iterate!

---

**Need help?** Check the GitHub Actions logs or raise an issue.
