output "droplet_id" {
    value = digitalocean_droplet.django_app.ipv4_address
}

output "db_host" {
    value = digitalocean_database_cluster.postgres.host
}
output "db_uri" {
    value = digitalocean_database_cluster.postgres.uri
    sensitive = true
}