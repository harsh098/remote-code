import json
import os.path
import pathlib
import shutil
import subprocess
from textwrap import dedent
from typing import Dict, Any

import click

working_dir = os.path.abspath(os.path.curdir)


def create_directory_structure():
    try:
        if not os.path.exists(os.path.join(working_dir, ".rcode")):
            os.makedirs(os.path.join(working_dir, ".rcode"))

        if not os.path.exists(os.path.join(working_dir, ".rcode", "tf")):
            os.makedirs(os.path.join(working_dir, ".rcode", "tf"))

        if not os.path.exists(os.path.join(working_dir, ".rcode", "ansible")):
            os.makedirs(os.path.join(working_dir, ".rcode", "ansible"))

        if not os.path.exists(os.path.join(working_dir, ".rcode", "ansible", "installer_playbook")):
            os.makedirs(os.path.join(working_dir, ".rcode", "ansible", "installer_playbook"))

        if not os.path.exists(os.path.join(working_dir, ".rcode", "ansible", "plugins")):
            os.makedirs(os.path.join(working_dir, ".rcode", "ansible", "plugins"))

    except PermissionError:
        click.echo(click.style("Permission Denied", fg="bright_red"))

    except OSError:
        click.echo(click.style("OS Error", fg="bright_red"))


def sync_or_create_infra(arch="amd64", aws_region="us-east-1", instance_type="t3.micro", **kwargs):
    """
    Provisions and Syncs Infra with Terraform.

    :param arch: Architecture of VM to provision
    :param aws_region: Region in which VM must be provisioned
    :param instance_type: Instance Type for VM
    :param kwargs: Extra arguments to be passed
    :return: None
    """
    create_directory_structure()
    create_tf_files()
    create_ansible_init_playbooks()
    run_terraform_provisioner(dir=pathlib.Path(working_dir), arch=arch, aws_region=aws_region,
                              instance_type=instance_type, **kwargs)


def create_tf_files():
    tf_path = os.path.join(working_dir, ".rcode", "tf")
    files = {
        "main.tf": dedent(r"""
        terraform {
          required_providers {
            aws = {
              source  = "hashicorp/aws"
              version = "5.38.0"
            }
            tls = {
              source  = "hashicorp/tls"
              version = "4.0.5"
            }
            local = {
              source  = "hashicorp/local"
              version = "2.4.1"
            }
            external = {
              source  = "hashicorp/external"
              version = "~>2.3.3"
            }
          }
        }
        
        provider "aws" {
          region = var.aws_region
        }
        
        data "aws_ami" "latest-ubuntu" {
          most_recent = true
          owners      = ["099720109477"] # Canonical
        
          filter {
            name   = "name"
            values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-${var.arch}-server-*"]
          }
        
          filter {
            name   = "virtualization-type"
            values = ["hvm"]
          }
        }
        
        data "external" "python_interpreter_binary" {
          program = ["bash", "${path.module}/get_python_binary.sh"]
        }
    """).strip("\n"),

        "create_ansible_inventory.tf": dedent(r"""
            resource "local_file" "ansible_inventory" {
              depends_on = [
                aws_instance.vm,
                local_file.ssh_private_key
              ]
              filename = abspath("${path.module}/../inventory.ini")
              content  = "ansible_arch=${var.arch}\n\n[vm]\n${aws_instance.vm.public_ip}  ansible_ssh_user=ubuntu ansible_ssh_private_key_file=${local_file.ssh_private_key.filename}"
            }
        """).strip("\n"),

        "vars.tf": dedent(
            r"""
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
            """
        ).strip("\n"),

        "vpc.tf": dedent(
            r"""
            resource "aws_security_group" "allow_ssh" {
              name = "allow_ssh"
            
              ingress {
                from_port = 22
                to_port   = 22
                protocol  = "tcp"
            
                cidr_blocks = ["0.0.0.0/0"] # TODO: Consider Securing this later
              }
            
              egress {
                from_port = 0
                to_port   = 0
                protocol  = "-1"
            
                cidr_blocks = ["0.0.0.0/0"] # TODO: Consider Securing this later
             }
            }
            """
        ).strip("\n"),

        "keys.tf": dedent(
            r"""
            resource "aws_key_pair" "ssh_public_key" {
              key_name   = "ssh_public_key"
              public_key = tls_private_key.ssh_key.public_key_openssh
            }
            
            resource "tls_private_key" "ssh_key" {
              algorithm = "RSA"
              rsa_bits  = 4096
            }
            
            resource "local_file" "ssh_private_key" {
              filename = abspath("${path.module}/../tfkey.pub")
              content  = tls_private_key.ssh_key.private_key_openssh
              provisioner "local-exec" {
                command = "chmod 400 ${path.module}/../tfkey.pub"
              }
            }
            """
        ).strip("\n"),

        "outputs.tf": dedent(
            r"""
            output "aws_instance_ip" {
              value = aws_instance.vm.public_ip
            }
            
            output "ssh_private_key_path" {
              value = local_file.ssh_private_key.filename
            }
            """
        ).strip("\n"),

        "vm.tf": dedent(
            r"""
            resource "aws_instance" "vm" {
              key_name                    = "ssh_public_key"
              ami                         = data.aws_ami.latest-ubuntu.id
              instance_type               = var.instance_type
              associate_public_ip_address = true
              vpc_security_group_ids      = [aws_security_group.allow_ssh.id]
              tags = {
                Name = "VsCodeServer"
              }
            }
            """
        ).strip("\n"),

        "get_python_binary.sh": dedent(
            r"""
            #!/usr/bin/env sh
            echo -e "{\n \"python\": \"$(which python || which python3)\"\n}" | jq .
            """
        ).strip("\n"),
    }
    try:
        for file_name, content in files.items():
            if os.path.exists(os.path.join(tf_path, file_name)):
                continue
            with open(os.path.join(tf_path, file_name), "w") as file:
                file.write(content)
                file.flush()

    except OSError:
        click.echo(click.style("OS Error", fg="bright_red"))

    except PermissionError:
        click.echo(click.style("Permission Error", fg="bright_red"))


def create_ansible_init_playbooks():
    ansible_dir = os.path.join(working_dir, ".rcode", "ansible")
    files = {
        "installer_playbook/configuration.yml": dedent("""
        ---
        - name: Install and configure Docker on Ubuntu
          become: true
        
          tasks:
            - name: Get Ubuntu facts
              setup:
        
            - name: Define variables based on facts
              set_fact:
                os_codename: "{{ ansible_lsb.codename }}"
                os_arch: "{{ ansible_arch }}"
        
            - name: Update package lists
              apt:
                update_cache: yes
        
            - name: Install prerequisite packages
              apt:
                name:
                  - apt-transport-https
                  - ca-certificates
                  - curl
                  - software-properties-common
        
            - name: Add Docker GPG key
              apt_key:
                url: https://download.docker.com/linux/ubuntu/gpg
                state: present
        
            - name: Add Docker repository
              apt_repository:
                repo: deb [arch={{ os_arch }}] https://download.docker.com/linux/ubuntu {{ os_codename }} stable
                state: present
        
            - name: Install Docker Engine
              apt:
                name: docker-ce
                state: present
        
            - name: Start and enable Docker service
              service:
                name: docker
                state: started
                enabled: yes

        """).strip("\n"),
        "installer_playbook/install_code_server.yml": dedent("""
        ---
        - name: Initial Setup
          import_playbook: configuration.yaml
        
        - name: Install and configure code-server
          become: true
        
          tasks:
        
            - name: Download and run code-server installation script
              shell: curl -fsSL https://code-server.dev/install.sh | sh
        
            - name: Enable and start code-server service
              service:
                name: code-server@{{ ansible_user }}
                state: started
                enabled: yes
        
            - name: Disable password authentication in config.yaml
              lineinfile:
                path: /home/{{ ansible_user }}/.config/code-server/config.yaml
                regexp: '^auth: password'
                line: 'auth: none'
                backup: yes
        
            - name: Restart code-server service
              service:
                name: code-server@{{ ansible_user }}
                state: restarted
        """),
    }
    try:
        for file_name, content in files.items():
            if os.path.exists(os.path.join(ansible_dir, file_name)):
                continue
            with open(os.path.join(ansible_dir, file_name), "w") as file:
                file.write(content)
                file.flush()

    except OSError:
        click.echo(click.style("OS Error", fg="bright_red"))

    except PermissionError:
        click.echo(click.style("Permission Error", fg="bright_red"))


def run_terraform_provisioner(dir: pathlib.Path = pathlib.Path(working_dir), arch="amd64", aws_region="us-east-1",
                              instance_type="t3.micro", **kwargs) -> int:
    tf_dir = dir / ".rcode" / "tf"
    os.chdir(tf_dir)
    terraform_init_process = subprocess.run(["terraform", f"-chdir={str(tf_dir)}", "init", "-no-color"])
    terraform_init_process.check_returncode()
    terraform_apply_command_vars = []
    vars = {
        "arch": arch,
        "aws_region": aws_region,
        "instance_type": instance_type,
        **kwargs
    }
    for var, val in vars.items():
        terraform_apply_command_vars.append("-var")
        terraform_apply_command_vars.append(f"{var}={val}")
    terraform_apply = subprocess.run(
        ["terraform", f"-chdir={str(tf_dir)}", "apply", "-auto-approve", "-no-color", *terraform_apply_command_vars])
    terraform_apply.check_returncode()
    os.chdir(dir)
    return terraform_apply.returncode


def get_terraform_values(dir: pathlib.Path = pathlib.Path(working_dir)) -> Dict[str, Any]:
    tf_dir = dir / ".rcode" / "tf"
    os.chdir(tf_dir)
    terraform_init_process = subprocess.run(["terraform", f"-chdir={str(tf_dir)}", "init", "-no-color"])
    terraform_init_process.check_returncode()
    terraform_outputs_command_status = os.system("terraform output -json | jq . | tee outputs.json")

    if (terraform_outputs_command_status >> 8):
        return dict()

    with open("outputs.json", "r") as f:
        terraform_outputs = json.load(f)
    os.remove("outputs.json")
    os.chdir(dir)
    return terraform_outputs


def destroy_terraform_infra(dir: pathlib.Path = pathlib.Path(working_dir)) -> int:
    tf_path = dir / ".rcode" / "tf"
    if not os.path.exists(tf_path):
        if os.path.exists(dir / ".rcode"):
            shutil.rmtree(dir / ".rcode")
        click.echo(click.style("No Infra to Delete", fg="green"))
        return 0
    os.chdir(tf_path)
    terraform_outputs = get_terraform_values(dir)
    if "aws_instance_ip" in terraform_outputs or "ssh_private_key_path" in terraform_outputs:
        terraform_destroy_process = subprocess.run(
            ["terraform", f"-chdir={str(tf_path)}", "destroy", "-auto-approve", "-no-color"])
        try:
            terraform_destroy_process.check_returncode()
        except subprocess.CalledProcessError:
            click.echo(click.style("Could not destroy infra, Config Corrupted", fg="bright_red"))
            return -1
    os.chdir(dir)
    shutil.rmtree(dir / ".rcode")
    return 0
