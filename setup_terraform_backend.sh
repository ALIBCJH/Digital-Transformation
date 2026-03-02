#!/bin/bash
# Setup script for Terraform S3 Backend and GitHub Secrets

set -e

echo "🚀 Terraform CI/CD Setup Script"
echo "================================"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Prompt for configuration
read -p "Enter S3 bucket name for Terraform state: " TF_STATE_BUCKET
read -p "Enter AWS region (default: eu-north-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-eu-north-1}

echo ""
echo "📦 Step 1: Creating S3 bucket for Terraform state..."

# Create S3 bucket
if aws s3 ls "s3://${TF_STATE_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${TF_STATE_BUCKET}" --region "${AWS_REGION}"
    echo "✅ S3 bucket created: ${TF_STATE_BUCKET}"
else
    echo "ℹ️  S3 bucket already exists: ${TF_STATE_BUCKET}"
fi

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket "${TF_STATE_BUCKET}" \
    --versioning-configuration Status=Enabled
echo "✅ Versioning enabled"

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket "${TF_STATE_BUCKET}" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'
echo "✅ Encryption enabled"

# Block public access
aws s3api put-public-access-block \
    --bucket "${TF_STATE_BUCKET}" \
    --public-access-block-configuration \
        "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
echo "✅ Public access blocked"

echo ""
echo "🔐 Step 2: Creating DynamoDB table for state locking..."

# Create DynamoDB table
if ! aws dynamodb describe-table --table-name terraform-state-lock --region "${AWS_REGION}" &> /dev/null; then
    aws dynamodb create-table \
        --table-name terraform-state-lock \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
        --region "${AWS_REGION}"
    echo "✅ DynamoDB table created: terraform-state-lock"
    echo "⏳ Waiting for table to become active..."
    aws dynamodb wait table-exists --table-name terraform-state-lock --region "${AWS_REGION}"
else
    echo "ℹ️  DynamoDB table already exists: terraform-state-lock"
fi

echo ""
echo "🔧 Step 3: Migrating Terraform state to S3..."

cd Infra/aws

# Backup existing state if it exists
if [ -f terraform.tfstate ]; then
    echo "📋 Backing up existing state file..."
    cp terraform.tfstate terraform.tfstate.backup-$(date +%Y%m%d-%H%M%S)
    echo "✅ Backup created"
fi

# Initialize with S3 backend
terraform init \
    -migrate-state \
    -backend-config="bucket=${TF_STATE_BUCKET}" \
    -backend-config="key=production/terraform.tfstate" \
    -backend-config="region=${AWS_REGION}"

echo "✅ Terraform state migrated to S3"

cd ../..

echo ""
echo "📝 Step 4: GitHub Secrets Setup Instructions"
echo "==========================================="
echo ""
echo "Add these secrets to your GitHub repository:"
echo "(Go to: Settings → Secrets and variables → Actions → New repository secret)"
echo ""
echo "Secret Name: TF_STATE_BUCKET"
echo "Secret Value: ${TF_STATE_BUCKET}"
echo ""
echo "Secret Name: DB_PASSWORD"
echo "Secret Value: <your-secure-database-password>"
echo ""
echo "Verify these existing secrets are configured:"
echo "- AWS_ROLE_ARN"
echo "- DJANGO_SECRET_KEY"
echo "- DATABASE_URL"
echo "- ALLOWED_HOSTS"
echo "- EC2_INSTANCE_ID (optional)"
echo ""

echo "✅ Setup Complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Add the GitHub secrets mentioned above"
echo "2. Update your IAM role with Terraform permissions (see TERRAFORM_CICD_SETUP.md)"
echo "3. Test the workflow by creating a PR"
echo "4. Merge to main to deploy!"
echo ""
echo "📚 For detailed instructions, see: TERRAFORM_CICD_SETUP.md"
