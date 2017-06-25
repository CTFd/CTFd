variable "aws_region" {
  default     = "us-east-1"
  description = "AWS region to use"
}

variable "subnet_ids" {
  type        = "list"
  default     = ["subnet-55908530", "subnet-a15226e9", "subnet-b62a1a8a", "subnet-4c9f2060", "subnet-15df684f"]
  description = "List of subnet ids to use (ex: [ \"subnet-xxxxxxxx\", \"subnet-xxxxxxxx\" ])"
}

variable "lb_security_group" {
  type        = "string"
  default     = "sg-064be977"
  description = "Security group for load balancer (ex: \"sg-xxxxxxxx\")"
}

variable "app_security_group" {
  type        = "string"
  default     = "sg-0b32907a"
  description = "Security group for application (ex: \"sg-xxxxxxxx\")"
}

variable "app_name" {
  type        = "string"
  default     = "ctfd"
  description = "Name of application (ex: \"ctfd\")"
}

variable "key_name" {
  type        = "string"
  default     = "ctf"
  description = "Existing key pair to use (ex: \"super-secret-key\")"
}

variable "db_user" {
  type        = "string"
  description = "user for db"
}

variable "db_pass" {
  type        = "string"
  description = "password from db"
}
