import pathlib
from typing import Dict, List, Any

import click
import yaml

from remote_code.cli import config_data, infra
from remote_code.plugins import cpp_plugin
from remote_code.plugins.installer import BaseInstaller

registry: Dict[str, BaseInstaller.__base__] = {
    "Cpp": cpp_plugin.CppInstallerClass
}

def build_plugin_playbooks():
    click.echo(click.style("Initialising Plugins", fg="cyan"))
    plugins_to_install = config_data.get_key_value_from_config("plugins") or []
    master_playbook_json = [
        {
            "import_playbook": str(pathlib.Path("installer_playbook") / "install_code_server.yml")
        }
    ]
    for plugin in plugins_to_install:
        plugin_installer_class = registry[plugin]()
        playbook_path = pathlib.Path("plugins") / plugin_installer_class.plugin_file
        master_playbook_json.append(
            {
                "import_playbook": str(playbook_path)
            }
        )
        plugin_installer_class.generate_config()
        plugin_installer_class.create_play_book()

    with open(pathlib.Path(infra.working_dir) / ".rcode" / "ansible" / "main.yml", "w+") as f:
        yaml.safe_dump(master_playbook_json, f, sort_keys=False)

