from unittest import TestCase

from functions import cli_converter


class TestConvert_command(TestCase):
    def test_delete_command(self):
        cmd = cli_converter.convert_command('delete.txt',
                                            'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/BulkChanger/input')
        self.assertEqual(cmd[0].body, '')
        self.assertEqual(cmd[0].action, 'delete')
        self.assertEqual(cmd[0].name, '1')
        self.assertEqual(cmd[0].path, 'firewall/policy')

    def test_device_settings(self):
        cmd = cli_converter.convert_command('device_settings.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API'
                                                                   '/BulkChanger/input')
        self.assertEqual(cmd[0].body, '{"admin-sport":"8443","admintimeout":"240"}')
        self.assertEqual(cmd[0].action, '')
        self.assertEqual(cmd[0].name, '')
        self.assertEqual(cmd[0].path, 'system/global')

    def test_policy_settings(self):
        cmd = cli_converter.convert_command('policy_settings.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                   'BulkChanger/input')
        self.assertEqual(cmd[0].body, '{"name":"dpo","accprofile":"super_admin","vdom":"root","password":'
                                      '"ENC AK16D3CKqjt+2aM/xf2ieZJcDoFdx2MhS5TxQWngTJi61s="}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'dpo')
        self.assertEqual(cmd[0].path, 'system/admin')
        self.assertEqual(cmd[1].body, '{"name":"dgu","accprofile":"super_admin","vdom":"root","password":'
                                      '"ENC AK1P+a8jSjvASnxe4qTPCFGtCkpZYhdUJDWC1IzLHQVRe0="}')
        self.assertEqual(cmd[1].action, 'edit')
        self.assertEqual(cmd[1].name, 'dgu')
        self.assertEqual(cmd[1].path, 'system/admin')

    def test_complex_object(self):
        cmd = cli_converter.convert_command('complex_object.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                  'BulkChanger/input')
        self.assertEqual(cmd[0].body,
                         '{\'json\':{"srcintf":[{"name":"internal"}],"dstintf":[{"name":"wan1"}],'
                         '"srcaddr":[{"name":"all"}],"dstaddr":[{"name":"all"}],"action":"accept",'
                         '"schedule":"always","service":[{"name":"ALL"}],"logtraffic":"all","comments":"fge test",'
                         '"nat":"enable"}}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, '0')
        self.assertEqual(cmd[0].path, 'firewall/policy')

    def test_interface_zone(self):
        cmd = cli_converter.convert_command('interface_zone.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                  'BulkChanger/input')
        self.assertEqual(cmd[0].body,
                         '{"name":"internet","interface":[{"interface-name":"wan1"},{"interface-name":"wan2"}]}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'internet')
        self.assertEqual(cmd[0].path, 'system/zone')

    def test_antivirus_profile(self):
        cmd = cli_converter.convert_command('antivirus_profile.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                     'BulkChanger/input')
        self.assertEqual(cmd[0].body,
                         '{"name":"av_standard","inspection-mode":"proxy","http":{"options":"scan"},'
                         '"ftp":{"options":"scan"},"imap":{"options":"scan"},"pop3":{"options":"scan"},'
                         '"smtp":{"options":"scan"},"mapi":{"options":"scan"}}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'av_standard')
        self.assertEqual(cmd[0].path, 'antivirus/profile')

    def test_app_conrol(self):
        cmd = cli_converter.convert_command('app_control.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                               'BulkChanger/input')
        self.assertEqual(cmd[0].body,
                         '{"name":"ac_standard","other-application-log":"enable","unknown-application-log":"enable",'
                         '"entries":[{"category":[{"id":"6"},{"id":"19"}]},{"category":[{"id":"2"},{"id":"3"},'
                         '{"id":"5"},{"id":"7"},{"id":"8"},{"id":"12"},{"id":"15"},{"id":"17"},{"id":"21"},'
                         '{"id":"22"},{"id":"23"},{"id":"25"},{"id":"26"},{"id":"28"},{"id":"29"},{"id":"30"},'
                         '{"id":"31"}],"action":"pass"}]}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'ac_standard')
        self.assertEqual(cmd[0].path, 'application/list')

    def test_ips_sensor(self):
        cmd = cli_converter.convert_command('ips_sensor.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                              'BulkChanger/input')
        self.assertEqual(cmd[0].body,
                         '{"name":"ips_outgoing","entries":[{"location":"client ","severity":"critical ",'
                         '"os":"Other Windows Linux MacOS ","status":"enable","log-packet":"enable","action":"block"},'
                         '{"location":"client ","severity":"high ","os":"Other Windows Linux MacOS "}]}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'ips_outgoing')
        self.assertEqual(cmd[0].path, 'ips/sensor')
        self.assertEqual(cmd[1].body,
                         '{"name":"ips_incoming","entries":[{"location":"server ","severity":"critical ",'
                         '"os":"Other Windows Linux ","status":"enable","log-packet":"enable","action":"block"},'
                         '{"location":"server ","severity":"high ","os":"Other Windows Linux "}]}')
        self.assertEqual(cmd[1].action, 'edit')
        self.assertEqual(cmd[1].name, 'ips_incoming')
        self.assertEqual(cmd[1].path, 'ips/sensor')

    def test_firewall_policy(self):
        cmd = cli_converter.convert_command('firewall_policy.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                   'BulkChanger/input')
        self.assertEqual(cmd[0].body,
                         '{\'json\':{"srcintf":[{"name":"internal"}],"dstintf":[{"name":"internet"}],'
                         '"srcaddr":[{"name":"all"}],"dstaddr":[{"name":"all"}],"action":"accept","schedule":"always",'
                         '"service":[{"name":"ALL"}],"logtraffic":"all","comments":"fge test","nat":"enable"}}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, '0')
        self.assertEqual(cmd[0].path, 'firewall/policy')

    def test_local_in_policy(self):
        cmd = cli_converter.convert_command('local_in_policy.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                   'BulkChanger/input')
        self.assertEqual(cmd[0].body, '{\'json\':{"intf":"internet","srcaddr":[{"name":"all"}],'
                                      '"dstaddr":[{"name":"all"}],"action":"accept","service":[{"name":"PING"},'
                                      '{"name":"IKE"},{"name":"ESP"},{"name":"HTTPS"},{"name":"fortisslvpn"}],'
                                      '"schedule":"always"}}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, '0')
        self.assertEqual(cmd[0].path, 'firewall/local-in-policy')
        self.assertEqual(cmd[1].body, '{\'json\':{"intf":"internet","srcaddr":[{"name":"grp_ffn-support"},'
                                      '{"name":"grp_forti-support"}],"dstaddr":[{"name":"all"}],"action":"accept",'
                                      '"service":[{"name":"SSH"},{"name":"fortiadmin"},{"name":"ALL_ICMP"}],'
                                      '"schedule":"always"}}')
        self.assertEqual(cmd[1].action, 'edit')
        self.assertEqual(cmd[1].name, '0')
        self.assertEqual(cmd[1].path, 'firewall/local-in-policy')
        self.assertEqual(cmd[2].body, '{\'json\':{"intf":"internet","srcaddr":[{"name":"all"}],'
                                      '"dstaddr":[{"name":"all"}],"service":[{"name":"ALL"}],"schedule":"always"}}')
        self.assertEqual(cmd[2].action, 'edit')
        self.assertEqual(cmd[2].name, '0')
        self.assertEqual(cmd[2].path, 'firewall/local-in-policy')

    def test_proxy_options(self):
        cmd = cli_converter.convert_command('proxy_options.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                 'BulkChanger/input')
        self.assertEqual(cmd[0].body, '{"name":"po_standard","http":{"ports":"80","options":"clientcomfort",'
                                      '"comfort-interval":"1","comfort-amount":"1024","post-lang":null},'
                                      '"ftp":{"ports":"21","options":"clientcomfort","comfort-interval":"1",'
                                      '"comfort-amount":"1024"},"imap":{"ports":"143","options":null},'
                                      '"mapi":{"ports":"135","options":null},"pop3":{"ports":"110","options":null},'
                                      '"smtp":{"ports":"25","options":null},"nntp":{"ports":"119","options":null},'
                                      '"im":{"options":null},"dns":{"ports":"53"}}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'po_standard')
        self.assertEqual(cmd[0].path, 'firewall/profile-protocol-options')
        self.assertEqual(cmd[1].body, '{"name":"po_standard","http":{"ports":"80","options":"clientcomfort",'
                                      '"comfort-interval":"1","comfort-amount":"1024","post-lang":null},'
                                      '"ftp":{"ports":"21","options":"clientcomfort","comfort-interval":"1",'
                                      '"comfort-amount":"1024"},"imap":{"ports":"143","options":null},'
                                      '"mapi":{"ports":"135","options":null},"pop3":{"ports":"110","options":null},'
                                      '"smtp":{"ports":"25","options":null},"nntp":{"ports":"119","options":null},'
                                      '"im":{"options":null},"dns":{"ports":"53"}}')
        self.assertEqual(cmd[1].action, 'edit')
        self.assertEqual(cmd[1].name, 'po_standard')
        self.assertEqual(cmd[1].path, 'firewall/profile-protocol-options')

    def test_rename(self):
        cmd = cli_converter.convert_command('rename.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                          'BulkChanger/input')
        self.assertEqual(cmd[0].body, '{"desc":"allow"}')
        self.assertEqual(cmd[0].action, 'rename')
        self.assertEqual(cmd[0].name, 'allow')
        self.assertEqual(cmd[0].path, 'webfilter/ftgd-local-cat/custom1')
        self.assertEqual(cmd[1].body, '{"desc":"block"}')
        self.assertEqual(cmd[1].action, 'rename')
        self.assertEqual(cmd[1].name, 'block')
        self.assertEqual(cmd[1].path, 'webfilter/ftgd-local-cat/custom2')

    def test_firewall_service(self):
        cmd = cli_converter.convert_command('firewall_service.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                    'BulkChanger/input')
        self.assertEqual(cmd[0].body, '{"name":"fortisslvpn","tcp-portrange":"10443"}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'fortisslvpn')
        self.assertEqual(cmd[0].path, 'firewall.service/custom')
        self.assertEqual(cmd[1].body, '{"name":"fortiadmin","tcp-portrange":"8443"}')
        self.assertEqual(cmd[1].action, 'edit')
        self.assertEqual(cmd[1].name, 'fortiadmin')
        self.assertEqual(cmd[1].path, 'firewall.service/custom')
        self.assertEqual(cmd[2].body, '{"name":"guest-services","member":[{"name":"HTTP"},{"name":"HTTPS"},'
                                      '{"name":"IMAP"},{"name":"IMAPS"},{"name":"POP3"},{"name":"POP3S"},'
                                      '{"name":"SMTP"},{"name":"SMTPS"},{"name":"FTP"},{"name":"PING"},'
                                      '{"name":"DNS"}]}')
        self.assertEqual(cmd[2].action, 'edit')
        self.assertEqual(cmd[2].name, 'guest-services')
        self.assertEqual(cmd[2].path, 'firewall.service/group')

    def test_ssl_vpn(self):
        cmd = cli_converter.convert_command('ssl_vpn.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                                    'BulkChanger/input')
        self.assertEqual(cmd[0].body, '')
        self.assertEqual(cmd[0].action, 'delete')
        self.assertEqual(cmd[0].name, 'full-access')
        self.assertEqual(cmd[0].path, 'vpn.ssl.web/portal')
        self.assertEqual(cmd[1].body, '')
        self.assertEqual(cmd[1].action, 'delete')
        self.assertEqual(cmd[1].name, 'tunnel-access')
        self.assertEqual(cmd[1].path, 'vpn.ssl.web/portal')
        self.assertEqual(cmd[2].body, '')
        self.assertEqual(cmd[2].action, 'delete')
        self.assertEqual(cmd[2].name, 'web-access')
        self.assertEqual(cmd[2].path, 'vpn.ssl.web/portal')
        self.assertEqual(cmd[3].body, '{"name":"none","web-mode":"enable","limit-user-logins":"enable",'
                                      '"user-bookmark":"disable","display-connection-tools":"disable",'
                                      '"display-history":"disable","display-status":"disable",'
                                      '"heading":"SSL-VPN Dummypage"}')
        self.assertEqual(cmd[3].action, 'edit')
        self.assertEqual(cmd[3].name, 'none')
        self.assertEqual(cmd[3].path, 'vpn.ssl.web/portal')
        self.assertEqual(cmd[4].body, '{"sslv3":"disable","servercert":"Fortinet_Factory","algorithm":"high",'
                                      '"idle-timeout":"3600","auth-timeout":"43200",'
                                      '"tunnel-ip-pools":[{"name":"net_sslvpn"}],"port":"443",'
                                      '"source-interface":[{"name":"internet"}],"source-address":[{"name":"all"}],'
                                      '"source-address6":[{"name":"all"}],"default-portal":"none"}')
        self.assertEqual(cmd[4].action, '')
        self.assertEqual(cmd[4].name, '')
        self.assertEqual(cmd[4].path, 'vpn.ssl/settings')

    def test_webfilter_profile(self):
        cmd = cli_converter.convert_command('webfilter_profile.txt', 'D:/Daten/Dropbox/Florian/50 FortiNet/REST API/'
                                                          'BulkChanger/input')
        self.assertEqual(cmd[0].body, '{"name":"wf_standard","override":{"ovrd-user-group":""},'
                                      '"web":{"log-search":"enable"},'
                                      '"ftgd-wf":{"options":"http-err-detail redir-block",'
                                      '"category-override":"140 141","filters":[{"id":"1","category":"26",'
                                      '"action":"block"},{"id":"2","category":"61","action":"block"},'
                                      '{"id":"3","category":"86","action":"block"},{"id":"4","category":"88",'
                                      '"action":"block"},{"id":"7","action":"block"},{"id":"6","category":"89"},'
                                      '{"id":"8","category":"140"},{"id":"9","category":"141","action":"block"}]},'
                                      '"comment":null,"log-all-url":null,"web-content-log":null,'
                                      '"web-filter-activex-log":null,"web-filter-command-block-log":null,'
                                      '"web-filter-cookie-log":null,"web-filter-applet-log":null,'
                                      '"web-filter-jscript-log":null,"web-filter-js-log":null,'
                                      '"web-filter-vbs-log":null,"web-filter-unknown-log":null,'
                                      '"web-filter-referer-log":null,"web-filter-cookie-removal-log":null,'
                                      '"web-url-log":null,"web-invalid-domain-log":null,"web-ftgd-err-log":null,'
                                      '"web-ftgd-quota-usage":null}')
        self.assertEqual(cmd[0].action, 'edit')
        self.assertEqual(cmd[0].name, 'wf_standard')
        self.assertEqual(cmd[0].path, 'webfilter/profile')
