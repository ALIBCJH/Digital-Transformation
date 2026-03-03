# Quick Migration Reference

## 🚀 Three Ways to Run Migrations

### 1. Automatic (Recommended)
**When:** Every push to `main`  
**Action:** Nothing - it happens automatically  
**Where:** GitHub Actions → Infrastructure & Deployment Pipeline

---

### 2. Manual via GitHub Actions
**When:** Need to run migrations without deploying  
**Action:** 
1. Go to GitHub repo → Actions tab
2. Select "Run Database Migrations"
3. Click "Run workflow"

**Options:**
- Leave empty for all migrations
- Specify app name for specific migrations
- Check "Create Superuser" if needed

---

### 3. Direct on EC2
**When:** Quick fixes, debugging, or emergency migrations  
**Action:** SSH into EC2 and run:

```bash
# Check if everything is configured
./check-db-config.sh

# Run all migrations
./migrate.sh

# Run specific app migrations
./migrate.sh core

# Check status
./migrate.sh --check

# Full deployment (migrate + collectstatic)
./migrate.sh --full
```

---

## 🔧 Quick Troubleshooting

### Container not found?
```bash
docker ps  # List running containers
docker-compose up -d  # Start if needed
```

### Database connection issues?
```bash
./check-db-config.sh  # Diagnose configuration
docker logs backend  # Check for errors
```

### SSM not working in GitHub Actions?
```bash
# On EC2:
sudo systemctl status amazon-ssm-agent
sudo systemctl restart amazon-ssm-agent
```

---

## 📝 Important Files

| File | Purpose |
|------|---------|
| `.github/workflows/infrastructure-and-deploy.yml` | Auto migrations on deploy |
| `.github/workflows/run-migrations.yml` | Manual migration workflow |
| `migrate.sh` | EC2 migration script |
| `check-db-config.sh` | EC2 config checker |
| `MIGRATION_GUIDE.md` | Full documentation |

---

## ⚡ Common Commands

```bash
# On EC2 (after SSH)
./check-db-config.sh              # Check configuration
./migrate.sh                      # Run migrations
./migrate.sh --check              # Check status
./migrate.sh --full               # Migrate + collectstatic
./migrate.sh core                 # Migrate specific app
./migrate.sh --rollback core 0010 # Rollback migration

# Docker commands (if needed)
docker ps                                    # List containers
docker logs backend                          # View logs
docker exec backend python manage.py migrate # Direct migration
```

---

## 🎯 First Time Setup

1. ✅ Push to `main` → Auto migration runs
2. ✅ Check GitHub Actions for success
3. ✅ SSH to EC2: `./check-db-config.sh`
4. ✅ Test API endpoints
5. ✅ Create superuser if needed:
   ```bash
   docker exec -it backend python manage.py createsuperuser
   ```

---

## 🔗 Environment Variables Required

### In GitHub Secrets
- `AWS_ROLE_ARN` - For AWS authentication
- `EC2_INSTANCE_ID` - Your EC2 instance
- `DJANGO_SECRET_KEY` - Django secret
- `DATABASE_URL` - Full database URL
- `ALLOWED_HOSTS` - Comma-separated hosts

### On EC2 (in docker-compose or .env)
- `DATABASE_URL` - Or individual DB_* variables
- `SECRET_KEY` - Django secret key
- `DEBUG` - Should be False in production
- `ALLOWED_HOSTS` - Your domain/IP addresses

---

**Need more details?** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
