import pathlib

import yaml

from remote_code.cli import infra


def get_config_data():
    file_path = pathlib.Path(infra.working_dir)  / ".rcode.yml"
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return data

def get_arch() -> str:
    data = get_config_data()
    return data["arch"]

def get_instance_type() -> str:
    data = get_config_data()
    return data["instance_type"]

def get_git_repo() -> str:
    data = get_config_data()
    return data["git_repo"]

def get_aws_region() -> str:
    data = get_config_data()
    return data["aws_region"]

def get_key_value_from_config(key: str) -> str:
    data = get_config_data()
    return data[key]

