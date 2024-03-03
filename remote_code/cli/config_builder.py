import pathlib
from typing import Any, Dict

import click
import yaml

from remote_code.cli import infra

class Option:
    def __init__(self, name: str, datatype: type, helper_text:str, default: Any=None):
        self.name = name
        if not self.name:
            raise ValueError("Keys Cannot Be Empty")
        self.helper_text = helper_text
        self.datatype = datatype
        self.default = default

    def get_input(self, config_dict: Dict[str, Any]):
        if self.name in config_dict:
            raise KeyError("Options With Same Keys")
        if self.default:
            config_dict[self.name] = click.prompt(self.helper_text, default=self.default, type=self.datatype)
        else:
            config_dict[self.name] = click.prompt(self.helper_text, type=self.datatype)

options = [
    Option(name="git_repo", helper_text="Enter URL of git repo", datatype=str),
    Option(name="instance_type", helper_text="AWS Instance Type", datatype=str, default="t3.micro"),
    Option(name="aws_region", helper_text="AWS Region", datatype=str, default="us-east-1"),
    Option(name="arch", helper_text="Architecture of VM", datatype=str, default="amd64")
]

def build_config():
    curdir = pathlib.Path(infra.working_dir)
    config_options = dict()
    for option in options:
        option.get_input(config_options)

    file_path = curdir / ".rcode.yml"
    with open(file_path, "w") as config_file:
        yaml.dump(config_options, config_file)

