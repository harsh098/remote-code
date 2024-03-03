resource "aws_key_pair" "ssh_public_key" {
  key_name   = "ssh_public_key"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

resource "local_file" "ssh_private_key" {
  filename = "${path.module}/../tfkey.pub"
  content  = tls_private_key.ssh_key.private_key_openssh
  provisioner "local-exec" {
    command = "chmod 400 ${path.module}/../tfkey.pub"
  }
}