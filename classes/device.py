import os
import urllib3
import socket
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
        self.timeout = 5
        self.connected = False
        self.customer = customer
        self.firmware = None
        self.serial = None
        self.reason = None
        self.fortimanager = None
        # infos for get info command
        self.av_db = None
        self.forticare = None
        self.fortiguard = None
        self.vdom_mode = None
        self.ssid = []
        self.ap_firmware = []
        self.ap_serial = []
        self.ap_name = []
        self.local_in = None

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
        for i in range(0, 3):
            count = os.system('ping -n 1 -w 1000 ' + self.ip + ' > nul')
        return True if count > 0 else False


    def check_ip(self) -> bool:
        # Check for DNS Names
        alpha = sum(c.isalpha() for c in self.ip)
        if alpha > 2:
            try:
                self.ip = socket.gethostbyname(self.ip)
            except:
                logging.warning('ip-check: cannot resolve dns name to ip')
                return True

        first_octet = int(self.ip.split('.')[0])
        second_octet = int(self.ip.split('.')[1])
        if first_octet == 10:
            return True
        if first_octet == 172 and second_octet >= 16 and second_octet <= 31:
            return True
        if first_octet == 192 and second_octet == 168:
            return True
        return False

    def check_duplicate(self, devices, index):
        i = 0
        while i < index:
            if (devices[i].serial == devices[index].serial):
                logging.warning('devices: found duplicate, remove from list')
                return True
            i += 1
        return False

