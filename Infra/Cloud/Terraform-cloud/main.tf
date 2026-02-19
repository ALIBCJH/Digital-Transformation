#Fetch the existing DigitalOcean SSH Key
data "digitalocean_ssh_key" "main"{
    name = var.ssh_key_name
}
# create a VPC (Private virtual cloud) so different resources can connect securely
resource "digitalocean_vpc" "app_vpc" {
    name = "digital transformation vpc"
    region = var_region
    }
    # Provision the postgress DB
    resource "digitalocean_database_cluster" "postgres"{
        name = "db-postgres-django"
        engine = "pg"
        version = "15"
        size = "db-s-1vcpu-1gb"
        region = var.region
        node_count = 1
        private_network_uuid = digitalocean_vpc.app_vpc.id
    }

    # Provision the Django Droplet
    resource "digitalocean_droplet" "django_app"{
        image = "ubuntu-24-04-x64"
        name = "django-backend"
        region = var.region
        size = "s-1vcpu-1gb"
        vpc_uuid = digitalocean_vpc.app_vpc.id
        ssh_keys = [data.digitalocean_ssh_key.main.id]
    }

    #Only Allow the Dropler to connect to the postgres DB
    resource "digitalocean_database_firewall" "db_firewall" {
        cluster_id = digitalocean_database_cluster.postgres.id

        rule {
            type = "droplet"
            value = digitalocean_droplet.django_app.id
        }
    }