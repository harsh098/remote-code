resource "local_file" "ansible_cfg" {
  depends_on = [
    aws_instance.vm,
    local_file.ssh_private_key
  ]
  filename = abspath("${path.module}/../ansible/ansible.cfg")
  content  = "[defaults]\ninventory=${abspath("${path.module}/../ansible/inventory/")}"
}

resource "local_file" "ansible_inventory" {
  depends_on = [
    aws_instance.vm,
    local_file.ssh_private_key
  ]
  filename = abspath("${path.module}/../ansible/inventory/inventory")
  content  = "[all:vars]\nansible_arch=${var.arch}\n\n[vm]\n${aws_instance.vm.public_ip}  ansible_ssh_user=ubuntu ansible_ssh_private_key_file=${local_file.ssh_private_key.filename}"
}