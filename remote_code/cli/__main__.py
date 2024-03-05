import os
import pathlib
from textwrap import dedent

import click

from remote_code import plugins
from remote_code.cli import infra, config_builder, config_data, ssh_utils
from remote_code.cli.ansible_wrapper import run_ansible_playbooks


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    click.echo(click.style("Welcome to Remote Code", fg="bright_blue"))
    if ctx.invoked_subcommand is None:
        click.echo(click.style("Run `rcode --help` to see a list of available commands", fg="bright_green"))
        click.echo(click.style("Run `rcode init` to set up a Cloud VM", fg="bright_green"))



@cli.command()
def create():
    """
    Creates AWS Infra for the VM
    """
    if not os.path.exists(pathlib.Path(infra.working_dir) / ".rcode.yml"):
        click.echo(click.style("No Configuration (.rcode.yml) File Found in current working directory\nRun `rcode init` to create a configuration file", fg="bright_red"))
        return
    click.echo(click.style("Creating Infra...", fg="green"))
    arch = config_data.get_arch()
    aws_region = config_data.get_aws_region()
    instance_type = config_data.get_instance_type()
    infra.sync_or_create_infra(arch, aws_region, instance_type)
    plugins.build_plugin_playbooks()
    run_ansible_playbooks()
    click.echo(click.style(
        dedent("""
        Your Remote Code VM is Up and Running.
        Run `rcode open` to open your CDE in Browser
        Alternatively you can run:-
        \t`rcode port-forward`
        and access your VM on the forwarded port
        """)
    ))

@cli.command()
def destroy():
    """
    Destroys AWS Infra for the VM
    """
    click.echo(click.style("Destorying Infra...", fg="yellow"))
    status = infra.destroy_terraform_infra(pathlib.Path(infra.working_dir))
    if not status:
        click.echo(click.style("Successfully Destroyed Infra", fg="yellow"))
    else:
        click.echo(click.style("There Were Problems Removing Infra", fg="bright_red"))

@cli.command()
def init():
    """
    Creates configuration file for .rcode.yml
    """
    config_builder.build_config()
    infra.create_directory_structure()
    infra.create_tf_files()
    infra.create_ansible_init_playbooks()
    plugins.build_plugin_playbooks()
    msg = dedent("""
    In the .rcode.yml add config options for your plugins as described in documentation which can be found at:
    <docs_URL>
    """)
    #TODO: Add Docs URL
    click.echo(click.style(msg, fg="blue"))

@cli.command()
@click.option("-r", "--remote-port", help="Remote Port on the VM", prompt=True, default=8080, show_default=True)
@click.option("-l", "--local-port", help="Local Port to forward to", prompt=True, default=8080, show_default=True)
def port_forward(local_port, remote_port):
    """
    Establishes tunnel between Remote-Code VM and your local machine
    """
    ssh_utils.port_forward_ssh(remote_port=remote_port, local_port=local_port)

@cli.command()
@click.option("-l", "--local-port", help="Local Port to forward to (Ensure this port is available)", prompt=True, default=8080, show_default=True)
def open(local_port):
    """
    Open In Browser
    """
    ssh_utils.port_forward_ssh(remote_port=8080, local_port=local_port, open_in_browser="/home/ubuntu/project", https=False)



if __name__ == '__main__':
    cli()
