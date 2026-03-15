variable "project_name" {
  type    = string
  default = "weather-logger"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "cluster_name" {
  type    = string
  default = "weather-logger-cluster"
}

variable "cluster_version" {
  type    = string
  default = "1.31"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "node_count" {
  type    = number
  default = 2
}
