# Blueprint of the aws Ec2 instances
resource "aws_ecs_task_definition" "garage_app" {
  family                   = "express-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn


  container_definitions = jsonencode([{
    name  = "node-express-app"
    image = var.container_image
    portMappings = [{
      containerPort = 3000
      hostPort      = 3000
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/express-app"
        " awslogs-region"       = "us-east-1"
        "awslogs-stream-prefix" = "ecs"
      }
    }
  }])
}
