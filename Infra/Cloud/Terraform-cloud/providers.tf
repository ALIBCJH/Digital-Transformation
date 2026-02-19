# the block intruct terrafrom to use the digitalocean provider
# and specify the version to use
# and the token to authenticate with the DigitalOcean API
# the token is stored in a variable to keep it secure
terraform {
    required_providers {
        digitalocean = {
            source = "digitalocean/digitalocean"
            version = "2.0"
        }
    }
}
provider  "digitalocean" {
    token = var.do_token
}