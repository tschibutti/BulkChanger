import os
import sys
import configparser, logging
from utils.singleton import Singleton


class Config(metaclass=Singleton):
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.file_path = os.path.join(os.path.abspath(os.path.dirname(sys.executable)), 'config.ini')
        else:
            self.file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'config.ini')
        logging.info('config: load config from file')
        self.configParser = configparser.ConfigParser()
        try:
            self.configParser.read(self.file_path)
            self.load_system_section()
        except:
            logging.error('config: file not found, create one with default settings')
            self.default_settings()
            self.configParser.read(self.file_path)
            self.load_system_section()

    def load_system_section(self):
        self.devices_folder = self.configParser['System']['devices_folder']
        self.backup_folder = self.configParser['System']['backup_folder']
        self.sslvpn_folder = self.configParser['System']['sslvpn_folder']
        self.firewall_user = self.configParser['System']['firewall_user']
        self.firewall_password = self.configParser['System']['firewall_password']
        self.sslvpn_user = self.configParser['System']['sslvpn_user']
        self.sslvpn_password = self.configParser['System']['sslvpn_password']
        self.firewall_ip = self.configParser['System']['firewall_ip']
        self.firewall_port = self.configParser['System']['firewall_port']
        self.firewall_firmware = self.configParser['System']['firewall_firmware']
        self.log_level = self.configParser['System']['log_level']
        self.backup_enable = self.configParser['System']['backup_enable']

    def default_settings(self):
        with open(self.file_path, 'w') as config_file:
            config_file.write('[System]\n')
            config_file.write('# DEBUG or INFO\n')
            config_file.write('log_level: info\n')
            config_file.write('# TRUE or FALSE\n')
            config_file.write('backup_enable: False\n')
            config_file.write('# leave user or password empty to specify during script\n')
            config_file.write('firewall_user: admin\n')
            config_file.write('firewall_password:\n')
            config_file.write('sslvpn_user: admin\n')
            config_file.write('sslvpn_password:\n')
            config_file.write('# leave ip or port empty to use devices_folder as source\n')
            config_file.write('firewall_ip: 1.1.1.1\n')
            config_file.write('firewall_port:\n')
            config_file.write('# specify the versions, where the command should be executed\n')
            config_file.write('# options are: 5.2 5.4 5.6 6.0\n')
            config_file.write('firewall_firmware: 5.2 5.4 5.6 6.0\n')
            config_file.write('# Format for paths: G:/Remotesupport/Firewall\n')
            config_file.write('devices_folder: C:/_Firewalls\n')
            config_file.write('backup_folder: C:/BulkChanger/backups\n')
            config_file.write('sslvpn_folder: C:/forticlient\n')
            config_file.close()