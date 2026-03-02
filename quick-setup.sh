#!/bin/bash
# Quick Setup Script for Terraform + CI/CD Pipeline

set -e

echo "🚀 Automated Infrastructure & Deployment Setup"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Prerequisites Check
echo "📋 Step 1: Checking Prerequisites..."
echo ""

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it first:"
    echo "   https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "⚠️  GitHub CLI not found (optional but recommended)"
    echo "   Install from: https://cli.github.com/"
else
    echo "✅ GitHub CLI found"
fi

echo "✅ AWS CLI found"
echo "✅ Terraform found"
echo ""

# Step 2: AWS Configuration
echo "🔧 Step 2: AWS Configuration"
echo ""
read -p "Enter your AWS region (default: eu-north-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-eu-north-1}

read -p "Enter S3 bucket name for Terraform state: " TF_STATE_BUCKET

if [ -z "$TF_STATE_BUCKET" ]; then
    echo "❌ S3 bucket name is required"
    exit 1
fi

echo ""
echo "Creating S3 bucket and DynamoDB table..."

# Create S3 bucket
if aws s3 ls "s3://${TF_STATE_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${TF_STATE_BUCKET}" --region "${AWS_REGION}"
    echo "✅ S3 bucket created"
else
    echo "ℹ️  S3 bucket already exists"
fi

# Configure bucket
aws s3api put-bucket-versioning \
    --bucket "${TF_STATE_BUCKET}" \
    --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
    --bucket "${TF_STATE_BUCKET}" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}
        }]
    }'

aws s3api put-public-access-block \
    --bucket "${TF_STATE_BUCKET}" \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

echo "✅ S3 bucket configured"

# Create DynamoDB table
if ! aws dynamodb describe-table --table-name terraform-state-lock --region "${AWS_REGION}" &> /dev/null; then
    aws dynamodb create-table \
        --table-name terraform-state-lock \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region "${AWS_REGION}"
    echo "✅ DynamoDB table created"
    aws dynamodb wait table-exists --table-name terraform-state-lock --region "${AWS_REGION}"
else
    echo "ℹ️  DynamoDB table already exists"
fi

# Step 3: Terraform Backend Setup
echo ""
echo "🏗️  Step 3: Initializing Terraform Backend..."
cd Infra/aws

if [ -f terraform.tfstate ]; then
    echo "📋 Backing up local state..."
    cp terraform.tfstate "terraform.tfstate.backup-$(date +%Y%m%d-%H%M%S)"
fi

terraform init \
    -migrate-state \
    -backend-config="bucket=${TF_STATE_BUCKET}" \
    -backend-config="key=production/terraform.tfstate" \
    -backend-config="region=${AWS_REGION}"

echo "✅ Terraform backend initialized"

cd ../..

# Step 4: GitHub Secrets
echo ""
echo "🔐 Step 4: GitHub Secrets Setup"
echo ""
echo "You need to add these secrets to your GitHub repository:"
echo "(Go to: Settings → Secrets and variables → Actions → New repository secret)"
echo ""
echo -e "${YELLOW}Required Secrets:${NC}"
echo "1. TF_STATE_BUCKET = ${TF_STATE_BUCKET}"
echo "2. DB_PASSWORD = <your-secure-database-password>"
echo "3. AWS_ROLE_ARN = <your-oidc-role-arn>"
echo "4. DJANGO_SECRET_KEY = <your-django-secret>"
echo "5. DATABASE_URL = <postgresql-connection-string>"
echo "6. ALLOWED_HOSTS = <your-ec2-ip-or-domain>"
echo ""

if command -v gh &> /dev/null; then
    read -p "Do you want to set GitHub secrets now? (y/N): " setup_secrets
    if [ "$setup_secrets" = "y" ] || [ "$setup_secrets" = "Y" ]; then
        echo ""
        gh secret set TF_STATE_BUCKET -b"${TF_STATE_BUCKET}"
        echo "✅ TF_STATE_BUCKET set"
        
        read -sp "Enter DB_PASSWORD: " db_pass
        echo ""
        gh secret set DB_PASSWORD -b"${db_pass}"
        echo "✅ DB_PASSWORD set"
        
        read -p "Enter AWS_ROLE_ARN: " role_arn
        gh secret set AWS_ROLE_ARN -b"${role_arn}"
        echo "✅ AWS_ROLE_ARN set"
        
        read -sp "Enter DJANGO_SECRET_KEY: " django_key
        echo ""
        gh secret set DJANGO_SECRET_KEY -b"${django_key}"
        echo "✅ DJANGO_SECRET_KEY set"
        
        read -p "Enter DATABASE_URL: " db_url
        gh secret set DATABASE_URL -b"${db_url}"
        echo "✅ DATABASE_URL set"
        
        read -p "Enter ALLOWED_HOSTS: " allowed_hosts
        gh secret set ALLOWED_HOSTS -b"${allowed_hosts}"
        echo "✅ ALLOWED_HOSTS set"
        
        echo ""
        echo "✅ All GitHub secrets configured!"
    fi
else
    echo "ℹ️  Set these secrets manually in GitHub repository settings"
fi

# Step 5: IAM Policy
echo ""
echo "📝 Step 5: IAM Policy Update"
echo ""
echo "Update your GitHub Actions IAM role with Terraform permissions."
echo "Policy document: Infra/aws/iam-policy-terraform-cicd.json"
echo ""
echo "Run this command to attach the policy:"
echo ""
echo -e "${YELLOW}aws iam put-role-policy --role-name YOUR-GITHUB-ACTIONS-ROLE \\"
echo "  --policy-name TerraformCICDAccess \\"
echo "  --policy-document file://Infra/aws/iam-policy-terraform-cicd.json${NC}"
echo ""

# Step 6: Test Terraform
echo ""
echo "🧪 Step 6: Testing Terraform Configuration..."
cd Infra/aws

read -sp "Enter database password for Terraform test: " tf_db_pass
echo ""

terraform validate
echo "✅ Terraform configuration is valid"

terraform plan -var="db_password=${tf_db_pass}"
echo "✅ Terraform plan successful"

cd ../..

# Summary
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "=============================================="
echo ""
echo "📚 Next Steps:"
echo "1. Review and update IAM policy (Step 5 above)"
echo "2. Verify GitHub secrets are set"
echo "3. Create a feature branch to test the pipeline:"
echo "   git checkout -b feature/test-cicd"
echo "   git push origin feature/test-cicd"
echo "4. Create a Pull Request to see Terraform plan"
echo "5. Merge to main to deploy infrastructure"
echo ""
echo "📖 Documentation:"
echo "- TERRAFORM_CICD_SETUP.md - Detailed setup guide"
echo "- DEPLOYMENT_ARCHITECTURE.md - Architecture overview"
echo ""
echo "🔗 Helpful Links:"
echo "- GitHub Actions: https://github.com/${GITHUB_REPOSITORY:-YOUR-REPO}/actions"
echo "- AWS Console: https://console.aws.amazon.com/"
echo ""
