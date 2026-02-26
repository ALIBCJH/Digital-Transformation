#Creating a VPC for secure private networking and displays it in DigitalOcean Dashbaord
resource "digitalocean_vpc" "app_vpc" {
    name = "digital-transition-vpc"
    region =  var.region
}

#Postresql Daatabase Cluster
resource "digitalocean_database_cluster" "postgres" {
    name = "db-postgres-django"
    engine = "pg"
    version = "15"
    size = "db-s-1vcpu-1gb"
    region = var.region
    node_count = 1
    private_network_uuid = digitalocean_vpc.app_vpc.id
}

#Database 
resource "digitalocean_database_db" dt_database {
    cluster_id = digitalocean_database_cluster.postgres.id
    name = "digital_transformation"
}

#Database user
resource "digitalocean_database_user" "dt_user" {
    cluster_id = digitalocean_database_cluster.postgres.id
    name = "dt_admin"
    }

# SSH Key Data Source
data "digitalocean_ssh_key" "main" {
  name = var.ssh_key_name
}

#Django Backend Droplet
resource "digitalocean_droplet" "django_app" {
    image = "docker-20-04"
    name =  "django-backend"
    region = var.region
    size = "s-2vcpu-2gb"
    vpc_uuid =  digitalocean_vpc.app_vpc.id
    ssh_keys = [data.digitalocean_ssh_key.main.id]

    user_data = templatefile("${path.module}/../Scripts/django-setup.sh", {
        db_host = digitalocean_database_cluster.postgres.private_host
        db_port = digitalocean_database_cluster.postgres.port
        db_name = digitalocean_database_db.dt_database.name
        db_user = digitalocean_database_user.dt_user.name
        db_password = digitalocean_database_user.dt_user.password
        django_secret_key = var.django_secret_key
        allowed_hosts = var.allowed_hosts
        frontend_ip = digitalocean_droplet.react_app.ipv4_address

    })
    tags = ["backend", "django", "production"]
}

#React Frontend Droplet
resource "digitalocean_droplet" "react_app" {
    image = "docker-20-04"
    name = "react-frontend"
    region = var.region
    size = "s-1vcpu-1gb"
    vpc_uuid = digitalocean_vpc.app_vpc.id
    ssh_keys = [data.digitalocean_ssh_key.main.id]

    user_data = templatefile("${path.module}/../Scripts/react-setup.sh", {
        backend_url = "http://${digitalocean_droplet.django_app.ipv4_address}:8000"
    })
    tags = ["frontend", "react", "production"]
    
    }

 #Database Firewall -Allow Django Droplet
 resource "digitalocean_database_firewall" "db_firewall" {
    cluster_id = digitalocean_database_cluster.postgres.id
     rule{
        type = "droplet"
        value = digitalocean_droplet.django_app.id
       
     } 
 }

#Firewall to allow traffic to Django Backend
   resource "digitalocean_firewall" "backend_firewall" {
    name = "django-backend-firewall"
    droplet_ids = [digitalocean_droplet.django_app.id]

    #SSH access
    inbound_rule {
        protocol = "tcp"
        port_range = "22"
        source_addresses = ["0.0.0.0/0", "::/0"]
    }
    #HTTP access
    inbound_rule {
        protocol = "tcp"
        port_range = "80"
        source_addresses = ["0.0.0.0/0", "::/0"]
    }
    #Django App port
    inbound_rule {
        protocol = "tcp"
        port_range = "8000"
        source_addresses = ["0.0.0.0/0", "::/0"]
    }
    #Allow all outbound traffic
    outbound_rule {
        protocol = "tcp"
        port_range = "1-65535"
        destination_addresses = ["0.0.0.0/0", "::/0"]
    }
    outbound_rule {
        protocol = "udp"
        port_range = "1-65535"
        destination_addresses = ["0.0.0.0/0", "::/0"]
    }

}

#Firewall to allow traffic to react frontend
resource "digitalocean_firewall" "frontend_firewall" {
    name = "react-frontend-firewall"

    droplet_ids = [digitalocean_droplet.react_app.id]

    #SSH Access
    inbound_rule {
        protocol = "tcp"
        port_range = "22"
        source_addresses = ["0.0.0.0/0", "::/0"]

    }
    #HTTP Access
    inbound_rule {
        protocol = "tcp"
        port_range = "80"
        source_addresses = ["0.0.0.0/0", "::/0"]

    }
    #Allow all outbound traffic
    outbound_rule {
        protocol = "tcp"
        port_range = "1-65535"
        destination_addresses = ["0.0.0.0/0", "::/0"]

    }
    #outbound rule for udp
    outbound_rule {
        protocol = "udp"
        port_range = "1-65535"
        destination_addresses = ["0.0.0.0/0", "::/0"]

    }
}
