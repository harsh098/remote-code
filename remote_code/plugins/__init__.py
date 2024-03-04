from remote_code.cli import config_data
from remote_code.plugins import cpp_plugin

registry = {
    "Cpp": cpp_plugin.CppInstallerClass
}

def build_plugin_playbooks():
    plugins_to_install = config_data.get_key_value_from_config("plugins") or []
    for plugin in plugins_to_install:
        plugin_installer_class = registry[plugin]()
        plugin_installer_class.generate_config()
        plugin_installer_class.create_play_book()
