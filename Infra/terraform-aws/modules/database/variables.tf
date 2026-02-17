variable "db_name" {
    description = "Initial Database name to create"
    type = string
    default = "appdb"

}
variable "engine" {
    description = "Database engine (pg for postgress)"
    type = string
    default = "pg"
}
variable "engine_version" {
    description = "Database engine version (ie 16)"
    type = string
    default = "16"
}
variable "region" {
    description = "Database region (ie nyc3)"
    type = string
    default = "nyc3"
}
variable "node_count" {
    description = "number of nodes in  the db cluster"
    type = number
    default = 1
}
variable "private_network_uuid"{
    description = "Vpc uuid to attach  the database to (for private networking)"
    type = string
    default = null
}
variable "tags" {
    description = "tags to apply to the database cluster"
    type = list(string)
    default = []
}
variable "maintanance_window_hour" {
    description = "Hour of the day maintenance window starts (0-23)"
    type = string
    default = "02:00:00"
}
variable "backup_restore_timestamp" {
    description =  "Timestamp to restore from  (ISO 8601 format)"
    type = string
    default = null
}
variable "db_users" {
    description = "Additional database users to creat (list of usernames)"
    type = list(string)
    default = []
}
variable "additional_databases" {
    description = "Additional databases to create within the cluster"
    type = list(string)
    default = []
}
variable "firewall_rules" {
    description = "Firewall rules to database access (list of droplets or CIDR Blocks)"
    type = list(object({
        type = string
        value = string
    }))
    default = []
}
variable "size" {
    description = "digitalocean ocean droplet size size"
    type = string
    default = "db-s-1vcpu-1gb"
}
variable "maintanance_window_day" {
    description = "Day of the wee maintanance window starts (ie sunday)"
    type = string
    default = "sunday"
}
