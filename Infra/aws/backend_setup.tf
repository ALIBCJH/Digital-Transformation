# 1. The S3 bucket (Fixed name: no underscores, globally unique)
resource "aws_s3_bucket" "terraform_state" {
    bucket        = "juma-terraform-state-storage-2026" 
    force_destroy = true
}

# 2. Enable versioning so you can recover old state files if needed
resource "aws_s3_bucket_versioning" "enabled" {
    bucket = aws_s3_bucket.terraform_state.id
    versioning_configuration {
        status = "Enabled"
    }
}

# 3. The DynamoDB table for state locking (Prevents two people from running terraform at once)
resource "aws_dynamodb_table" "terraform_locks" {
    name         = "terraform-state-locking"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "LockID"

    attribute {
        name = "LockID"
        type = "S"
    }
}