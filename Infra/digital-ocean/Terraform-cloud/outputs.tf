output "django_droplet_ip"{
    value = digitalocean_droplet.django_app.ipv4_address
    description = "The public address for Django app Droplet"
}

output "react_droplet_ip" {
    value = digitalocean_droplet.react_app.ipv4_address
    description =  "The public address for React app droplet"
}

output "backend_url" {
    value = "http://${digitalocean_droplet.django_app.ipv4_address}:8000"
    description = "Django backend url"
}

output "frontend_url" {
    value  = "http://${digitalocean_droplet.react_app.ipv4_address}"
    description =  "React frontend url"
}

output "backend_admin_url" {
    value =  "http://${digitalocean_droplet.django_app.ipv4_address}:8000/admin"
    description = "The django admin panel url"
}

output "db_connection_info" {
    value = {
        host = digitalocean_database_cluster.db_cluster.postgres.private_host
        port = digitalocean_database_cluster.db_cluster.postgres.port
        database = digitalocean_database_db.dt_database.name
        user = digitalocean_database_user.dt_user.name
    }
    description = "Database connection information"
    sensitive = true
}
output "ssh_commands" {
    value = {
        django_backend = "ssh roots@${digitalocean_droplet.django_app.ipv4_address}"
        react_frontend = "ssh roots@${digitalocean_droplet.react_app.ipv4_address}"

    }
    description = "SSH command to connect with the droplets"
}