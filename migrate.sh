#!/bin/bash
#
# Database Migration Script for EC2 Instance
# This script runs Django migrations inside the backend Docker container
#
# Usage:
#   ./migrate.sh                    # Run all migrations
#   ./migrate.sh core               # Run migrations for specific app
#   ./migrate.sh --check            # Check migration status
#   ./migrate.sh --rollback core 0001  # Rollback to specific migration
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to find backend container
find_backend_container() {
    print_info "Finding backend container..."
    
    # Try different container name patterns
    CONTAINER_ID=$(docker ps -qf "name=backend" | head -n 1)
    
    if [ -z "$CONTAINER_ID" ]; then
        CONTAINER_ID=$(docker ps --format '{{.Names}}' | grep -iE 'backend|django' | head -n 1)
        if [ -n "$CONTAINER_ID" ]; then
            CONTAINER_ID=$(docker ps -qf "name=$CONTAINER_ID")
        fi
    fi
    
    if [ -z "$CONTAINER_ID" ]; then
        print_error "Backend container not found!"
        print_info "Available containers:"
        docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
        exit 1
    fi
    
    CONTAINER_NAME=$(docker inspect --format='{{.Name}}' "$CONTAINER_ID" | sed 's/\///')
    print_success "Found container: $CONTAINER_NAME ($CONTAINER_ID)"
    echo "$CONTAINER_ID"
}

# Function to check database connectivity
check_database() {
    local container_id=$1
    print_info "Checking database connectivity..."
    
    if docker exec "$container_id" python manage.py check --database default > /dev/null 2>&1; then
        print_success "Database connection successful"
        return 0
    else
        print_error "Database connection failed"
        return 1
    fi
}

# Function to show migration status
show_migration_status() {
    local container_id=$1
    local app=$2
    
    print_info "Current migration status:"
    echo ""
    
    if [ -n "$app" ]; then
        docker exec "$container_id" python manage.py showmigrations "$app"
    else
        docker exec "$container_id" python manage.py showmigrations
    fi
}

# Function to run migrations
run_migrations() {
    local container_id=$1
    local app=$2
    
    print_info "Running database migrations..."
    
    if [ -n "$app" ]; then
        print_info "Migrating app: $app"
        docker exec "$container_id" python manage.py migrate "$app" --noinput
    else
        print_info "Migrating all apps"
        docker exec "$container_id" python manage.py migrate --noinput
    fi
    
    print_success "Migrations completed successfully!"
}

# Function to create migrations
make_migrations() {
    local container_id=$1
    local app=$2
    
    print_info "Making new migrations..."
    
    if [ -n "$app" ]; then
        docker exec "$container_id" python manage.py makemigrations "$app"
    else
        docker exec "$container_id" python manage.py makemigrations
    fi
}

# Function to rollback migration
rollback_migration() {
    local container_id=$1
    local app=$2
    local migration=$3
    
    if [ -z "$app" ] || [ -z "$migration" ]; then
        print_error "Both app name and migration number are required for rollback"
        echo "Usage: $0 --rollback <app> <migration>"
        exit 1
    fi
    
    print_warning "Rolling back $app to migration $migration..."
    docker exec "$container_id" python manage.py migrate "$app" "$migration"
    print_success "Rollback completed"
}

# Function to collect static files
collect_static() {
    local container_id=$1
    
    print_info "Collecting static files..."
    docker exec "$container_id" python manage.py collectstatic --noinput --clear
    print_success "Static files collected"
}

# Main script logic
main() {
    echo "=================================================="
    echo "   Django Database Migration Script"
    echo "=================================================="
    echo ""
    
    # Find the backend container
    CONTAINER_ID=$(find_backend_container)
    echo ""
    
    # Check database connectivity
    if ! check_database "$CONTAINER_ID"; then
        print_error "Cannot proceed without database connection"
        exit 1
    fi
    echo ""
    
    # Parse command line arguments
    case "${1:-}" in
        --check)
            show_migration_status "$CONTAINER_ID" "${2:-}"
            ;;
        --rollback)
            show_migration_status "$CONTAINER_ID" "$2"
            echo ""
            rollback_migration "$CONTAINER_ID" "$2" "$3"
            echo ""
            show_migration_status "$CONTAINER_ID" "$2"
            ;;
        --makemigrations)
            make_migrations "$CONTAINER_ID" "${2:-}"
            ;;
        --collectstatic)
            collect_static "$CONTAINER_ID"
            ;;
        --full)
            # Run full deployment sequence
            show_migration_status "$CONTAINER_ID"
            echo ""
            run_migrations "$CONTAINER_ID" "${2:-}"
            echo ""
            collect_static "$CONTAINER_ID"
            echo ""
            show_migration_status "$CONTAINER_ID"
            ;;
        --help|-h)
            cat << EOF
Usage: $0 [OPTION] [APP_NAME]

Run Django database migrations inside the backend Docker container.

Options:
    (no args)              Run all pending migrations
    APP_NAME               Run migrations for specific app only
    --check [APP_NAME]     Show migration status without running
    --rollback APP MIGRATION  Rollback to specific migration
    --makemigrations [APP] Create new migrations
    --collectstatic        Collect static files
    --full [APP_NAME]      Run migrations + collectstatic + show status
    --help, -h             Show this help message

Examples:
    $0                          # Run all migrations
    $0 core                     # Run migrations for 'core' app
    $0 --check                  # Check migration status
    $0 --check core             # Check status for 'core' app
    $0 --rollback core 0010     # Rollback core to migration 0010
    $0 --full                   # Full deployment (migrate + collectstatic)
    $0 --makemigrations core    # Create new migrations for 'core' app

EOF
            exit 0
            ;;
        *)
            # Default: run migrations (with optional app name)
            show_migration_status "$CONTAINER_ID" "${1:-}"
            echo ""
            run_migrations "$CONTAINER_ID" "${1:-}"
            echo ""
            print_info "Updated migration status:"
            show_migration_status "$CONTAINER_ID" "${1:-}"
            ;;
    esac
    
    echo ""
    print_success "Operation completed successfully!"
    echo "=================================================="
}

# Run main function
main "$@"
