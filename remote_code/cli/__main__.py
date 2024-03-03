import os
import pathlib

import click

from remote_code.cli import infra, config_builder


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(click.style("Welcome to Remote Code", fg="bright_blue"))


@cli.command()
@click.option("-a", "--arch", default="amd64", help="VM Architecture [amd64|arm64] defualt=amd64")
@click.option("-A", "--aws-region", default="us-east-1", help="Specify AWS Region default=us-east-1")
@click.option("-I", "--instance_type", default="t3.micro", help="AWS Instance Type to create default=t3.micro")
def create(arch, aws_region, instance_type):
    """
    Creates AWS Infra for the VM
    """
    if not os.path.exists(pathlib.Path(infra.working_dir) / ".rcode.yml"):
        click.echo(click.style("No Configuration (.rcode.yml) File Found in current working directory\nRun `rcode init` to create a configuration file", fg="bright_red"))
        return
    click.echo(click.style("Creating Infra...", fg="green"))
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


if __name__ == '__main__':
    cli()
