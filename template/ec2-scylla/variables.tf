variable "owner" {
    default = "sso.<name>"
}

variable "placement_group_name" {
    default = "sso.pg-<name>"
}

variable "region" {
    default = "us-east-2"
}
 
variable "keypair_name" {
    default = "sso.keypair-<name>"
}

variable "public_key_location" {
    default = "../key.pub"
}

variable "private_key_location" {
    default = "../key"
}

# ============ Scylla Cluster ===============

variable "cluster_size" {
    default = "1"
}

variable "cluster_sg_name" {
    default = "sso.cluster-sg-<name>"
}

variable "cluster_instance_type" {
    default = "i3.2xlarge"
}

variable "cluster_name" {
    default = "sso.cluster-<name>"
}

variable "cluster_user" {
    default = "centos"
}

variable "scylla_ami" {
    #  4.4.0
    default = "ami-0908bf554a8e333db"
}


# ============ Prometheus instance ===============

variable "prometheus_name" {
    default = "sso.prometheus-<name>"
}

variable "prometheus_sg_name" {
    default = "sso.prometheus-sg-<name>"
}

variable "prometheus_instance_type" {
    default = "c5.xlarge"
}

variable "prometheus_ami" {
    # Ubuntu Server 18.04 
    default = "ami-0dd9f0e7df0f0a138"
}

# ============ Load Generators  ===============

variable "loadgenerator_instance_type" {
    default = "c5.4xlarge"
}

variable "loadgenerator_name" {
    default = "sso.loadgenerator-<name>"
}

variable "loadgenerator_sg_name" {
    default = "sso.loadgenerator-sg-<name>"
}

variable "loadgenerator_size" {
    default = "1"
}

variable "loadgenerator_ami" {
    default = "ami-0996d3051b72b5b2c"
}

variable "loadgenerator_user" {
    default = "ubuntu"
}

