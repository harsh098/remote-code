import time
import webbrowser
from textwrap import dedent
from typing import Optional

import click
import paramiko.ssh_exception
from sshtunnel import SSHTunnelForwarder

from remote_code.cli import infra


import paramiko
import socket
def __is_ssh_reachable(hostname, port=22, username="ubuntu", pkey=None, timeout=2):
  """
  Checks if a host is reachable by SSH using a private key.

  Args:
      hostname: The hostname or IP address of the remote server.
      port (int, optional): The SSH port (default 22).
      username (str, optional): The username for SSH authentication (default "your_username").
      pkey (paramiko.RSAKey or paramiko.DSSAKey, optional): The private key object for authentication.
      timeout (int, optional): The connection timeout in seconds (default 2).

  Returns:
      bool: True if the host is reachable, False otherwise.
  """
  client = paramiko.SSHClient()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  try:
    if pkey is not None:
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(hostname, port=port, username=username, pkey=pkey, timeout=timeout)
    else:
      client.connect(hostname, port=port, username=username, timeout=timeout)
      client.close()
    return True
  except (paramiko.SSHException, socket.timeout) as e:
    return False
  except paramiko.ssh_exception.NoValidConnectionsError:
      return False


def is_ssh_reachable() -> bool:
    """
    Checks if Remote Code VM is reacheable via SSH on port 22
    Returns:
        bool: True if host is reacheable else return False
    """
    tf_data = infra.get_terraform_values()
    host = tf_data["aws_instance_ip"]["value"]
    key_path = tf_data["ssh_private_key_path"]["value"]
    pkey = paramiko.RSAKey.from_private_key_file(key_path)
    return __is_ssh_reachable(hostname=host, pkey=pkey, username="ubuntu")

def port_forward_ssh(remote_port: int, local_port: int, open_in_browser: Optional[str]=None, https: bool=False):
    """
    Implements Port Forward Functionality in Python.
    :param remote_port: int
    :param local_port: int
    :param open_in_browser: Optional[int]
    :param https: bool: if True uses https:// else use http:// if False
    :return:
    """
    tf_data = infra.get_terraform_values()
    ssh_host = tf_data["aws_instance_ip"]["value"]
    ssh_key = tf_data["ssh_private_key_path"]["value"]
    try:
        with SSHTunnelForwarder(
            ssh_address_or_host=ssh_host,
            ssh_pkey=ssh_key,
            remote_bind_address=("127.0.0.1", remote_port),
            local_bind_address=("127.0.0.1", local_port),
            ssh_username="ubuntu"
        ) as server:
            server.start()
            click.echo(click.style(
                dedent(f"""
                Starting SSH Tunnel from {ssh_host}:{remote_port} to 127.0.0.1:{local_port} 
                To stop the tunnel press Ctrl-C
                """), fg="blue"
            ))
            if open_in_browser!=None:
                url = ("https://" if https else "http://") + f"127.0.0.1:{local_port}/" + (f"?folder={open_in_browser}" if open_in_browser!="" else "")
                click.echo(click.style(f"Opening in Browser:-\n\t{url}", fg="blue"))
                webbrowser.open(url)
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        click.echo(click.style("Stopping SSH Tunnel", fg="red"))
        server.stop()
    except paramiko.ssh_exception.NoValidConnectionsError:
        click.echo(click.style("Invalid Connection Details", fg="red"))


