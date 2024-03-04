import os.path
import pathlib

from ansible_runner import Runner, RunnerConfig

from remote_code.cli import infra

ansible_dir = pathlib.Path(infra.working_dir) / ".rcode" / "ansible"
playbook_path = ansible_dir / "main.yml"
inventory_dir = ansible_dir / "inventory"
private_data_dir = ansible_dir / ".tmp"



def run_ansible_playbooks():
    if not os.path.exists(private_data_dir):
        os.makedirs(private_data_dir)

    runner_config = RunnerConfig(
        private_data_dir=str(private_data_dir),
        playbook=str(playbook_path),
        inventory=str(inventory_dir)
    )
    runner_config.prepare()
    runner = Runner(config=runner_config)
    runner.run()
