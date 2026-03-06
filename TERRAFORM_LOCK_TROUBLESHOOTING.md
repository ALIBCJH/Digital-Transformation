# Terraform State Lock Troubleshooting Guide

## 🚨 Problem: State Lock Error

When you see this error during deployment:
```
Error: Error acquiring the state lock
Lock Info:
  ID:        4b2df095-9028-c760-c866-4e0809f679bd
  Operation: OperationTypePlan
  Who:       runner@runnervm0kj6c
```

This means a previous Terraform run was interrupted and left the state locked.

## ✅ Solutions (3 Options)

### Option 1: Use GitHub Actions Manual Unlock (Recommended)

1. Go to **Actions** tab in your GitHub repository
2. Click on **Infrastructure & Deployment Pipeline**
3. Click **Run workflow** button (top right)
4. Enter the **Lock ID** from the error message in the `force_unlock` field
   - Example: `4b2df095-9028-c760-c866-4e0809f679bd`
5. Click **Run workflow**
6. This will unlock the state and you can retry your deployment

### Option 2: Automatic Retry (Built-in)

The workflow now automatically:
- Detects stale locks during plan
- Attempts to unlock them
- Retries the plan operation

Simply **re-run the failed workflow** from GitHub Actions.

### Option 3: Manual Unlock via AWS CLI (Advanced)

If you have AWS credentials configured locally:

```bash
cd Infra/aws
terraform init
terraform force-unlock -force <LOCK_ID>
```

Replace `<LOCK_ID>` with the ID from the error message.

## 🛡️ Prevention

The workflow now includes:
- ✅ Automatic lock detection and cleanup
- ✅ 30-minute timeout to prevent stuck locks
- ✅ Cleanup steps on failure
- ✅ Manual unlock option via workflow dispatch

## 📋 Current Lock Status

To check if there's an active lock:

```bash
# Via AWS DynamoDB Console
# Table: terraform-state-locking
# Look for items with LockID field
```

## ⚠️ When to Manually Unlock

**Safe to force unlock if:**
- ✅ You're sure no other Terraform process is running
- ✅ The lock is from a cancelled/failed GitHub Action
- ✅ Lock age > 30 minutes old

**DO NOT force unlock if:**
- ❌ Another person might be running Terraform
- ❌ Lock is recent (< 5 minutes old)
- ❌ Unsure if operation is still running

## 🔧 Emergency Commands

### Check DynamoDB for locks:
```bash
aws dynamodb scan \
  --table-name terraform-state-locking \
  --region eu-north-1
```

### Clear a specific lock:
```bash
aws dynamodb delete-item \
  --table-name terraform-state-locking \
  --key '{"LockID": {"S": "juma-terraform-state-storage-2026/digital-transformation/terraform.tfstate-md5"}}' \
  --region eu-north-1
```

## 📞 Support

If issues persist:
1. Check the [GitHub Actions logs](https://github.com/ALIBCJH/Digital-Transformation/actions)
2. Verify no local Terraform processes are running
3. Confirm AWS credentials are valid
4. Review [Terraform State Lock documentation](https://developer.hashicorp.com/terraform/language/state/locking)
