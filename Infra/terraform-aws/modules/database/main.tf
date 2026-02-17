# modules/database/main.tf
# DigitalOcean managed database module

resource "digitalocean_database_cluster" "postgres" {
  name       = var.db_name
  engine     = var.engine
  version    = var.engine_version
  size       = var.size
  region     = var.region
  node_count = var.node_count
  
  private_network_uuid = var.private_network_uuid
  
  tags = var.tags

  # Maintenance window
  maintenance_window {
    day  = var.maintenance_window_day
    hour = var.maintenance_window_hour
  }

  # Backup restore (only if timestamp provided)
  dynamic "backup_restore" {
    for_each = var.backup_restore_timestamp != null ? [1] : []
    content {
      database_name     = var.db_name
      backup_created_at = var.backup_restore_timestamp
    }
  }
}

# Default database
resource "digitalocean_database_db" "default" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_name
}

# Additional databases
resource "digitalocean_database_db" "additional" {
  count      = length(var.additional_databases)
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.additional_databases[count.index]
}

# Additional database users
resource "digitalocean_database_user" "additional" {
  count      = length(var.db_users)
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.db_users[count.index]
}

# Database firewall
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id

  dynamic "rule" {
    for_each = var.firewall_rules
    content {
      type  = rule.value.type
      value = rule.value.value
    }
  }
}

# Connection pool
resource "digitalocean_database_connection_pool" "postgres_pool" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "${var.db_name}-pool"
  mode       = "transaction"
  size       = 25
  db_name    = digitalocean_database_db.default.name
  user       = digitalocean_database_cluster.postgres.user
}