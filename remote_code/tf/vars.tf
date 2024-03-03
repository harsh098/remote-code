variable "instance_type" {
  type        = string
  description = "The EC2 Instance Type to Provision"
  default     = "t3.micro"
}

variable "aws_region" {
  type        = string
  description = "The Region in which to Provision all the Resources"
  default     = "us-east-1"
}

variable "arch" {
  type        = string
  description = "The Architecture for the EC2 Instance. Valid Values = [amd64|arm64]"
  default     = "amd64"
}