#!/bin/bash
#
# Robust Database Migration Script for GitHub Actions
# Runs via AWS SSM on EC2 instance with comprehensive health checks and retry logic
#
set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       DATABASE MIGRATION - ROBUST EXECUTION               ║"
echo "╚═══════════════════════════════════════════════════════════╝"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  DATABASE MIGRATION EXECUTION"
echo "═══════════════════════════════════════════════════════════"
echo "Started at: $(date)"
echo ""

echo "📋 Step 1/6: Initial wait for container stability (60s)..."
sleep 60
echo "✅ Wait completed"
echo ""

echo "📋 Step 2/6: Locating backend container..."
CONTAINER_ID=$(docker ps -q --filter 'name=backend' --filter 'status=running')
if [ -z "$CONTAINER_ID" ]; then
  echo "❌ ERROR: Backend container not found"
  echo "Available containers:"
  docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}'
  exit 1
fi
CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$CONTAINER_ID" | sed 's/\///')
echo "✅ Found container: $CONTAINER_NAME (ID: $CONTAINER_ID)"
echo ""

echo "📋 Step 3/6: Verifying container health..."
HEALTH_RETRIES=0
MAX_HEALTH_RETRIES=9
while [ $HEALTH_RETRIES -lt $MAX_HEALTH_RETRIES ]; do
  HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_ID" 2>/dev/null || echo 'none')
  if [ "$HEALTH_STATUS" = "healthy" ] || [ "$HEALTH_STATUS" = "none" ]; then
    echo "✅ Container health status: $HEALTH_STATUS"
    break
  fi
  HEALTH_RETRIES=$((HEALTH_RETRIES + 1))
  echo "⏳ Container health: $HEALTH_STATUS (check $HEALTH_RETRIES/$MAX_HEALTH_RETRIES)"
  if [ $HEALTH_RETRIES -lt $MAX_HEALTH_RETRIES ]; then sleep 10; fi
done
if [ $HEALTH_RETRIES -eq $MAX_HEALTH_RETRIES ] && [ "$HEALTH_STATUS" != "healthy" ] && [ "$HEALTH_STATUS" != "none" ]; then
  echo "⚠️  WARNING: Container health check timeout, proceeding anyway..."
fi
echo ""

echo "📋 Step 4/6: Testing database connectivity (with retry)..."
DB_RETRIES=0
MAX_DB_RETRIES=3
DB_CONNECTED=false
while [ $DB_RETRIES -lt $MAX_DB_RETRIES ]; do
  if docker exec "$CONTAINER_ID" python manage.py check --database default 2>&1; then
    echo "✅ Database connection successful"
    DB_CONNECTED=true
    break
  fi
  DB_RETRIES=$((DB_RETRIES + 1))
  if [ $DB_RETRIES -lt $MAX_DB_RETRIES ]; then
    echo "⚠️  Database connection failed (attempt $DB_RETRIES/$MAX_DB_RETRIES), retrying in 15s..."
    sleep 15
  fi
done
if [ "$DB_CONNECTED" != "true" ]; then
  echo "❌ ERROR: Database connection failed after $MAX_DB_RETRIES attempts"
  echo "Environment check:"
  docker exec "$CONTAINER_ID" env | grep -E 'DB_|DATABASE' || echo 'No DB env vars found'
  echo "Container logs (last 50 lines):"
  docker logs "$CONTAINER_ID" --tail 50
  exit 1
fi
echo ""

echo "📋 Step 5/6: Checking current migration status..."
docker exec "$CONTAINER_ID" python manage.py showmigrations --plan | head -n 20
echo ""

echo "📋 Step 6/6: Executing database migrations..."
echo "⚙️  Running: python manage.py migrate --noinput"
if docker exec "$CONTAINER_ID" python manage.py migrate --noinput 2>&1; then
  echo ""
  echo "✅ Migrations completed successfully"
  echo ""
  echo "📊 Post-migration status:"
  docker exec "$CONTAINER_ID" python manage.py showmigrations | grep -E '^\[X\]' | wc -l | xargs echo "Applied migrations:"
  echo ""
  echo "🎯 Collecting static files..."
  docker exec "$CONTAINER_ID" python manage.py collectstatic --noinput --clear 2>&1 | tail -n 5
  echo ""
  echo "═══════════════════════════════════════════════════════════"
  echo "✅ MIGRATION SUCCESSFUL"
  echo "═══════════════════════════════════════════════════════════"
  echo "Completed at: $(date)"
  exit 0
else
  echo ""
  echo "❌ ERROR: Migration command failed"
  echo ""
  echo "🔍 Diagnostics:"
  echo "Container logs (last 100 lines):"
  docker logs "$CONTAINER_ID" --tail 100
  echo ""
  echo "Container status:"
  docker ps -a | grep backend
  exit 1
fi
