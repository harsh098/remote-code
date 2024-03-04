import os
import pathlib
from textwrap import dedent

import click

from remote_code import plugins
from remote_code.cli import infra, config_builder, config_data


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(click.style("Welcome to Remote Code", fg="bright_blue"))


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


if __name__ == '__main__':
    cli()
