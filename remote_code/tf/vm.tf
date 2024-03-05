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