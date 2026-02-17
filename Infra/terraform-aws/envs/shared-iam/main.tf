#Creating Group for the team
resource "aws_iam_group" "admins" {
 name = "infra-admin"
}
resource "aws_iam_group" "developers" {
 name = "developers"
}


