#!/bin/bash
#
# Environment Variables Setup Script for EC2
# This script helps configure database connection for migrations
#

set -e

echo "=========================================="
echo "  Database Configuration Checker"
echo "=========================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker is installed and running
echo "1. Checking Docker..."
if command_exists docker; then
    echo "   ✅ Docker is installed"
    if docker ps >/dev/null 2>&1; then
        echo "   ✅ Docker is running"
    else
        echo "   ❌ Docker daemon is not running"
        echo "   Run: sudo systemctl start docker"
        exit 1
    fi
else
    echo "   ❌ Docker is not installed"
    exit 1
fi
echo ""

# Check if backend container is running
echo "2. Checking Backend Container..."
BACKEND_CONTAINER=$(docker ps --filter "name=backend" --format "{{.Names}}" | head -n 1)
if [ -n "$BACKEND_CONTAINER" ]; then
    echo "   ✅ Backend container is running: $BACKEND_CONTAINER"
    CONTAINER_ID=$(docker ps -qf "name=backend" | head -n 1)
else
    echo "   ❌ Backend container is not running"
    echo "   Run: docker-compose up -d"
    exit 1
fi
echo ""

# Check environment variables in container
echo "3. Checking Environment Variables..."
echo ""

check_env_var() {
    local var_name=$1
    local value=$(docker exec "$CONTAINER_ID" printenv "$var_name" 2>/dev/null || echo "")
    
    if [ -n "$value" ]; then
        # Mask sensitive values
        if [[ "$var_name" == *"PASSWORD"* ]] || [[ "$var_name" == *"SECRET"* ]] || [[ "$var_name" == *"KEY"* ]]; then
            echo "   ✅ $var_name: ****"
        else
            echo "   ✅ $var_name: $value"
        fi
        return 0
    else
        echo "   ❌ $var_name: NOT SET"
        return 1
    fi
}

# Check DATABASE_URL
if check_env_var "DATABASE_URL"; then
    echo "   ℹ️  Using DATABASE_URL for connection"
elif check_env_var "DB_HOST" && check_env_var "DB_NAME"; then
    echo "   ℹ️  Using individual DB_* variables"
    check_env_var "DB_USER"
    check_env_var "DB_PASSWORD"
    check_env_var "DB_PORT"
    check_env_var "DB_ENGINE"
else
    echo "   ❌ Database configuration is incomplete"
    echo ""
    echo "   Required: Either DATABASE_URL or (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)"
    exit 1
fi
echo ""

check_env_var "SECRET_KEY"
check_env_var "ALLOWED_HOSTS"
check_env_var "DEBUG"
echo ""

# Test database connectivity
echo "4. Testing Database Connection..."
if docker exec "$CONTAINER_ID" python manage.py check --database default 2>&1 | grep -q "System check identified no issues"; then
    echo "   ✅ Database connection successful"
else
    echo "   ❌ Database connection failed"
    echo ""
    echo "   Troubleshooting steps:"
    echo "   1. Verify RDS endpoint is correct"
    echo "   2. Check security group allows EC2 → RDS on port 5432"
    echo "   3. Verify database credentials"
    echo "   4. Check if RDS instance is running"
    exit 1
fi
echo ""

# Test Django setup
echo "5. Testing Django Configuration..."
if docker exec "$CONTAINER_ID" python manage.py check 2>&1 | grep -q "System check identified no issues"; then
    echo "   ✅ Django configuration is valid"
else
    echo "   ⚠️  Django configuration has warnings"
fi
echo ""

# Show migration status
echo "6. Current Migration Status..."
echo ""
docker exec "$CONTAINER_ID" python manage.py showmigrations | head -n 20
echo ""
echo "   (Use './migrate.sh --check' to see full status)"
echo ""

# Final summary
echo "=========================================="
echo "  ✅ Configuration Check Complete"
echo "=========================================="
echo ""
echo "Your environment is properly configured!"
echo ""
echo "Next steps:"
echo "  • Run migrations: ./migrate.sh"
echo "  • Check full status: ./migrate.sh --check"
echo "  • View logs: docker logs $BACKEND_CONTAINER"
echo ""
