output "aws_instance_ip" {
  value = aws_instance.vm.public_ip
}

output "ssh_private_key_path" {
  value = local_file.ssh_private_key.filename
}