resource "aws_ecs_cluster" "main" {
    name = "turbofan-cluster1"

    configuration {
        execute_command_configuration {
            logging = "DEFAULT"
        }
    }
}