import time
import webbrowser
from textwrap import dedent

import click
import paramiko.ssh_exception
from sshtunnel import SSHTunnelForwarder

from remote_code.cli import infra

def port_forward_ssh(remote_port: int, local_port: int, open_in_browser: bool=False, https: bool=False):
    ssh_host = infra.get_terraform_values()["aws_instance_ip"]["value"]
    ssh_key = infra.get_terraform_values()["ssh_private_key_path"]["value"]
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
            if open_in_browser:
                url = ("https://" if https else "http://") + f"127.0.0.1:{local_port}/"
                click.echo(click.style(f"Opening in Browser:-\n\thttps://127.0.0.1:{local_port}/", fg="blue"))
                webbrowser.open(url)
            while True:
                time.sleep(1)

    except KeyboardInterrupt:
        click.echo(click.style("Stopping SSH Tunnel", fg="red"))
        server.stop()
    except paramiko.ssh_exception.NoValidConnectionsError:
        click.echo(click.style("Invalid Connection Details", fg="red"))


