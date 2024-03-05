import pathlib
from typing import Dict, Any

import yaml

import remote_code.cli.config_data
from remote_code.cli import infra
from remote_code.plugins.installer import BaseInstaller


class PythonInstallerClass(BaseInstaller):
    inventory_file = "python_inventory"
    plugin_file = "python.yml"

    def keys_handler(self) -> Dict[str, Any]:
        keys = {}
        python_version = remote_code.cli.config_data.get_key_value_from_config("python_version")
        if python_version is not None:
            keys["python_version"] = python_version

        return keys

    def generate_config(self):
        keys = self.keys_handler()
        path_to_plugin_inventory_file = pathlib.Path(
            infra.working_dir) / ".rcode" / "ansible" / "inventory" / self.inventory_file
        with open(path_to_plugin_inventory_file, "w+") as f:
            for key, val in keys.items():
                f.write(f"{key}={val}\n")

    def create_play_book(self):
        content = [
            {
                "name": "Install Python DevTools on Ubuntu",
                "hosts": "vm",
                "become": True,
                "tasks": [
                    {
                        "name": "Get Ubuntu facts",
                        "setup": None
                    },
                    {
                        "name": "Define variables based on facts",
                        "set_fact": {
                            "os_codename": "{{ ansible_lsb.codename }}",
                            "os_arch": "{{ ansible_arch }}"
                        }
                    },
                    {
                        "name": "Update package lists",
                        "apt": {
                            "update_cache": "yes"
                        }
                    },
                    {
                        "name": "Install latest-stable Version of Python",
                        "apt": {
                            "name": [
                                "python3",
                                "python3-dev",
                                "python3-poetry",
                                "python3-venv"
                            ],
                            "state": "present"
                        }
                    },
                    {
                        "name": "Install A Specific Version of Python (Version 3.9 and later supported) if Specified",
                        "apt": {
                            "name": [
                                "python{{ python_version }}",
                                "python{{ python_version }}-dev"
                            ],
                            "state": "present"
                        },
                        "when": "python_version is defined",
                        "ignore_errors": True
                    }
                ]
            }
        ]
        path_to_plugin_file = pathlib.Path(infra.working_dir) / ".rcode" / "ansible" / "plugins" / self.plugin_file
        with open(path_to_plugin_file, "w+") as f:
            yaml.safe_dump(content, f, sort_keys=False)
