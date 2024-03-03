import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, List

import click
import inquirer
import yaml

from remote_code.cli import infra

@dataclass
class MultiOptionType:
    key: str
    prompt: str
    choices: List[str] = field(default_factory=lambda: [])
    def get_value(self, config_dict: Dict[str, Any]):
        questions = [
            inquirer.Checkbox(
                self.key,
                message= self.prompt + "\nUse Left/Right Keys to Select/Deselect and Up/Down Keys to Navigate",
                choices= self.choices
            )
        ]
        answer = inquirer.prompt(questions)
        config_dict[self.key] = answer[self.key] or []

@dataclass
class PluginType(MultiOptionType):
    choices: List[str] = field(default_factory=lambda: ["Cpp", "Maven", "Go", "GCC-C/C++", "Clang-C/C++", "OpenJDK", "NodeJS", "MySQL", "Postgres", "Python3", "MongoDB"])



class Option:
    def __init__(self, name: str, datatype: type, helper_text:str, default: Any=None):
        self.name = name
        if not self.name:
            raise ValueError("Keys Cannot Be Empty")
        self.helper_text = helper_text
        self.datatype = datatype
        self.default = default

    def get_input(self, config_dict: Dict[str, Any]):
        if self.datatype == MultiOptionType:
            raise TypeError("Not a supported Type")
        if MultiOptionType not in self.datatype.__bases__:
            if self.name in config_dict:
                raise KeyError("Options With Same Keys")
            if self.default:
                config_dict[self.name] = click.prompt(self.helper_text, default=self.default, type=self.datatype)
            else:
                config_dict[self.name] = click.prompt(self.helper_text, type=self.datatype)
        else:
            input_field = self.datatype(key=self.name, prompt=self.helper_text)
            input_field.get_value(config_dict)



options = [
    Option(name="git_repo", helper_text="Enter URL of git repo", datatype=str),
    Option(name="instance_type", helper_text="AWS Instance Type", datatype=str, default="t3.micro"),
    Option(name="aws_region", helper_text="AWS Region", datatype=str, default="us-east-1"),
    Option(name="arch", helper_text="Architecture of VM", datatype=str, default="amd64"),
    Option(name="plugins", helper_text="Select Plugins to Install", datatype=PluginType, default=[])
]

def build_config():
    curdir = pathlib.Path(infra.working_dir)
    config_options = dict()
    for option in options:
        option.get_input(config_options)

    file_path = curdir / ".rcode.yml"
    with open(file_path, "w") as config_file:
        yaml.dump(config_options, config_file)

