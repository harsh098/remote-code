import pathlib
from typing import Dict, Any

import yaml

import remote_code.cli.config_data
from remote_code.cli import infra
from remote_code.plugins.installer import BaseInstaller


class CppInstallerClass(BaseInstaller):
    inventory_file = "gcc_inventory.ini"
    plugin_file = "cpp.yml"
    def keys_handler(self) -> Dict[str, Any]:
        keys = {}
        gcc_version = remote_code.cli.config_data.get_key_value_from_config("gcc_version")
        if gcc_version is not None:
            keys["gcc_version"] = gcc_version

        return keys

    def generate_config(self):
        keys = self.keys_handler()
        path_to_plugin_inventory_file = pathlib.Path(infra.working_dir) / ".rcode" / "ansible" / self.inventory_file
        with open(path_to_plugin_inventory_file, "w+") as f:
            for key, val in keys.items():
                f.write(f"{key}={val}\n")

    def create_play_book(self):
        content = [
            {
                "name": "Install and configure C/C++ (GCC) DevTools on Ubuntu",
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
                        "name": "Install g++ if version explicitly defined",
                        "apt": {
                            "name": [
                                "g++={{gcc_version}}"
                            ],
                            "state": "present"
                        },
                        "when": "gcc_version is defined"
                    },
                    {
                        "name": "Install latest g++",
                        "apt": {
                            "name": [
                                "g++"
                            ],
                            "state": "present"
                        },
                        "when": "gcc_version is not defined"
                    },
                    {
                        "name": "Install build-essentials",
                        "apt": {
                            "apt": {
                                "name": [
                                    "build-essential"
                                ],
                                "state": "present"
                            }
                        }
                    }
                ]
            }
        ]
        path_to_plugin_file = pathlib.Path(infra.working_dir) / ".rcode" / "ansible" / "plugins" / self.plugin_file
        with open(path_to_plugin_file, "w+") as f:
            yaml.safe_dump(content, f, sort_keys=False)

