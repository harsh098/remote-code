from abc import ABC, abstractmethod


class BaseInstaller(ABC):
    @abstractmethod
    def keys_handler(self):
        """
        Acquire Keys From .rcode.yml
        :return:
        """
        pass
    @abstractmethod
    def generate_config(self):
        """
        Generate JSON for ansible playbook
        :return:
        """
        pass
    @abstractmethod
    def create_play_book(self):
        """
        Generate Playbook in ansible/plugins directory
        :return:
        """
        pass
