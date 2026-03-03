# Database Migration Guide

This guide explains how to run Django database migrations to your AWS RDS instance using various methods.

## 🎯 Overview

Your application now has **three ways** to run database migrations:

1. **Automated Migrations** - Runs automatically on every deployment
2. **Manual GitHub Actions Workflow** - Trigger migrations from GitHub UI
3. **Direct EC2 Script** - Run migrations directly on the EC2 instance

---

## 1️⃣ Automated Migrations (Recommended)

### How It Works

Every time you push to the `main` branch, the deployment workflow automatically:
1. Deploys your application
2. Runs database migrations
3. Collects static files
4. Verifies the deployment

### When It Runs

- ✅ Automatically on every push to `main`
- ✅ After successful deployment
- ✅ Before the deployment is marked complete

### What Gets Migrated

- All pending Django migrations across all apps
- Static files are collected automatically

### Monitoring

Check the GitHub Actions tab to see:
- Migration status
- Migration output logs
- Any errors during migration

---

## 2️⃣ Manual GitHub Actions Workflow

### When to Use

- Run migrations without deploying code
- Migrate specific Django apps
- Create superuser after migration
- Test migrations before full deployment

### How to Trigger

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Run Database Migrations** workflow
4. Click **Run workflow**
5. Fill in the options:
   - **Instance ID**: Leave empty to use default
   - **Migration App**: Specify app name or leave empty for all
   - **Create Superuser**: Check if needed

### Workflow File

Located at: `.github/workflows/run-migrations.yml`

### Example Use Cases

```bash
# Run all migrations
Leave all fields empty, click "Run workflow"

# Migrate only the 'core' app
Migration App: core

# Run migrations and create superuser
Create Superuser: ✓ (checked)
```

### Requirements

- AWS credentials configured (via OIDC)
- EC2 instance running
- Backend container deployed
- Database accessible from EC2

---

## 3️⃣ Direct EC2 Script

### When to Use

- Quick migrations during debugging
- Local testing on EC2
- When you have SSH access
- Emergency migrations

### Setup

1. SSH into your EC2 instance:
   ```bash
   ssh -i juma-key.pem ubuntu@<YOUR_EC2_IP>
   ```

2. Navigate to your project directory or upload the script:
   ```bash
   cd /home/ubuntu
   # Upload migrate.sh if not present
   chmod +x migrate.sh
   ```

### Usage Examples

#### Run All Migrations
```bash
./migrate.sh
```

#### Run Migrations for Specific App
```bash
./migrate.sh core
```

#### Check Migration Status
```bash
./migrate.sh --check
```

#### Check Status for Specific App
```bash
./migrate.sh --check core
```

#### Full Deployment (Migrate + Collectstatic)
```bash
./migrate.sh --full
```

#### Rollback to Specific Migration
```bash
./migrate.sh --rollback core 0010
```

#### Create New Migrations
```bash
./migrate.sh --makemigrations core
```

#### Collect Static Files Only
```bash
./migrate.sh --collectstatic
```

#### Show Help
```bash
./migrate.sh --help
```

### Script Features

- ✅ Automatically finds backend container
- ✅ Checks database connectivity
- ✅ Shows migration status before/after
- ✅ Color-coded output
- ✅ Error handling
- ✅ Multiple operation modes

---

## 🔧 Troubleshooting

### Problem: Migrations Fail with Connection Error

**Solution:**
1. Check if EC2 can reach RDS:
   ```bash
   # On EC2 instance
   telnet <RDS_ENDPOINT> 5432
   ```

2. Verify security group rules allow EC2 → RDS on port 5432

3. Check environment variables in Docker container:
   ```bash
   docker exec <container_id> env | grep DB
   ```

### Problem: Container Not Found

**Solution:**
1. List running containers:
   ```bash
   docker ps
   ```

2. If backend isn't running:
   ```bash
   cd /home/ubuntu
   docker-compose up -d
   ```

3. Check container logs:
   ```bash
   docker logs <container_name>
   ```

### Problem: Migration Conflicts

**Solution:**
1. Check migration status:
   ```bash
   ./migrate.sh --check
   ```

2. If conflicts exist, you may need to:
   - Merge migrations manually
   - Use `--fake` flag (advanced)
   - Consult Django migration documentation

### Problem: Permission Denied on migrate.sh

**Solution:**
```bash
chmod +x migrate.sh
```

### Problem: GitHub Actions Fails with SSM Timeout

**Solution:**
1. Verify SSM agent is running on EC2:
   ```bash
   sudo systemctl status amazon-ssm-agent
   ```

2. If not running:
   ```bash
   sudo systemctl start amazon-ssm-agent
   ```

3. Check IAM role attached to EC2 has SSM permissions

---

## 🔒 Security Best Practices

### Environment Variables

Never commit these to Git:
- `DB_PASSWORD`
- `DJANGO_SECRET_KEY`
- `DATABASE_URL`

Store them in:
- GitHub Secrets (for workflows)
- `.env` file on EC2 (for direct script)
- AWS Systems Manager Parameter Store (optional)

### Database Backups

Always backup before major migrations:

```bash
# On RDS, enable automated backups
# Or create manual snapshot via AWS Console
```

### Testing

1. Test migrations on staging first
2. Review migration SQL:
   ```bash
   docker exec <container> python manage.py sqlmigrate core 0001
   ```

3. Use `--plan` to see what will be migrated:
   ```bash
   docker exec <container> python manage.py migrate --plan
   ```

---

## 📊 Migration Status Indicators

When checking migration status:

```
[X] migration_name    # Applied
[ ] migration_name    # Not applied
```

---

## 🚀 Quick Start Checklist

For first-time setup:

- [ ] Push code to `main` branch (auto runs migrations)
- [ ] Verify migrations ran successfully in GitHub Actions
- [ ] SSH into EC2 and verify:
  ```bash
  docker ps  # Backend container is running
  docker logs <container>  # No migration errors
  ```
- [ ] Test API endpoints to confirm database is working
- [ ] Create superuser if needed:
  ```bash
  docker exec -it <container> python manage.py createsuperuser
  ```

---

## 📝 Configuration Files

### Workflow: Automatic Deployment
File: `.github/workflows/infrastructure-and-deploy.yml`
- Runs on push to `main`
- Includes migration step
- Collects static files

### Workflow: Manual Migrations
File: `.github/workflows/run-migrations.yml`
- Manual trigger only
- Flexible options
- Can target specific apps

### Script: Direct Migrations
File: `migrate.sh`
- Runs on EC2 instance
- Multiple operation modes
- Interactive and scriptable

---

## 🔗 Related Documentation

- [Django Migrations Documentation](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [Docker Exec Command](https://docs.docker.com/engine/reference/commandline/exec/)

---

## 💡 Tips

1. **Monitor migrations during deployment**: Watch GitHub Actions logs
2. **Use manual workflow for testing**: Test migrations before merging
3. **Keep migrate.sh on EC2**: Useful for quick debugging
4. **Check migration status regularly**: Especially after deployments
5. **Document custom migrations**: Add comments to migration files

---

## 🆘 Getting Help

If you encounter issues:

1. Check migration logs in GitHub Actions
2. Review container logs: `docker logs <container>`
3. Verify database connectivity from EC2
4. Check security group rules
5. Review this guide's troubleshooting section

---

**Last Updated**: March 2026  
**Maintained By**: DevOps Team
