import os
import urllib3
from requests import RequestException
from requests import Session
from json import JSONDecodeError
from utils.config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import logging

class Device:
    def __init__(self, customer, ip, port):
        self.ip = ip
        self.port = port
        self.session = None
        self.timeout = 2
        self.connected = False
        self.customer = customer
        self.online = 0
        self.firmware = None
        self.serial = None
        self.reason = None
        self.vdom = []
        self.fortimanager = False
        # infos for get info command
        self.av_db = None
        self.forticare = None
        self.fortiguard = None
        self.uptime = None
        self.vdom_mode = None
        self.ssid = []
        self.ap_firmware = []
        self.ap_serial = []
        self.ap_name = []

    def login(self, user, password):
        self.session = Session()
        bodyhash = {'username': user, 'secretkey': password}
        try:
            self.session.post('https://' + self.ip + ':' + self.port + '/logincheck', data=bodyhash,
                              verify=False, timeout=self.timeout)
            req = self.session.get('https://' + self.ip + ':' + self.port + '/api/v2/cmdb/system/status?vdom=root')
            try:
                req = req.json()
            except JSONDecodeError:
                logging.warning('login: wrong username or password')
                return
            if req['http_status'] == 200:
                logging.debug('login: successful')
                self.firmware = req['version']
                self.serial = req['serial']
                self.connected = True
            else:
                logging.warning('login: wrong username or password, skip device')
        except RequestException:
            logging.warning('login: timed out, skip device')
            self.connected = False
            return
        for cookie in self.session.cookies:
            try:
                if cookie.name == 'ccsrftoken':
                    csrftoken = cookie.value[1:-1]
                    self.session.headers.update({'X-CSRFTOKEN': csrftoken})
            except:
                logging.error('csrftoken not found')

    def logout(self):
        self.session.post('https://' + self.ip + ':' + self.port + '/logout')
        self.connected = False
        logging.debug('logout: successful')

    def firmware_check(self):
        if not self.firmware[1:4] in Config().firewall_firmware:
            logging.warning('device: firmware condition not meet, skip device')
            self.reason = 'firmware mismatch'
            self.connected = False
        else:
            logging.debug('device: firmware condition meet')

    def ping(self):
        self.online = os.system('ping -n 1 -w 1500 ' + self.ip + ' > nul')
        self.online = os.system('ping -n 1 -w 1500 ' + self.ip + ' > nul')
        self.online = os.system('ping -n 1 -w 1500 ' + self.ip + ' > nul')


