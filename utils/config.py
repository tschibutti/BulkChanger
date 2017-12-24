import configparser, logging
from utils.singleton import Singleton


class Config(metaclass=Singleton):
    def __init__(self):
        file_path = 'C:/BulkChanger/config.ini'
        logging.info('config: load config from file')
        self.configParser = configparser.ConfigParser()
        try:
            self.configParser.read(file_path)
            self.load_system_section()
        except:
            logging.error('config: error, abort execution')
            print('error: check log file for details')
            exit()

    def load_system_section(self):
        self.devices_folder = self.configParser['System']['devices_folder']
        self.input_folder = self.configParser['System']['input_folder']
        self.output_folder = self.configParser['System']['output_folder']
        self.backup_folder = self.configParser['System']['backup_folder']
        self.sslvpn_folder = self.configParser['System']['sslvpn_folder']
        self.firewall_user = self.configParser['System']['firewall_user']
        self.firewall_password = self.configParser['System']['firewall_password']
        self.firewall_ip = self.configParser['System']['firewall_ip']
        self.firewall_port = self.configParser['System']['firewall_port']
        self.firewall_firmware = self.configParser['System']['firewall_firmware']
        self.log_level = self.configParser['System']['log_level']
