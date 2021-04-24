import os
import tempfile
import pexpect
import time
import sys
from datetime import datetime

SSH_OPTIONS = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'

class System():
    def __init__(self, type, ip, mac_address, username, password, lcd_rotation, token):
        self.type = type
        self.ip = ip
        self.mac_address = mac_address
        self.username = username
        self.password = password
        self.lcd_rotation = lcd_rotation
        self.token = token

    def _git_download(self):
        self._ssh('git clone https://github.com/makerhafen/MAAPS.git ; cd MAAPS ; git pull')
        self._ssh('cd MAAPS/client ; sudo pip3 install -r requirements.txt')
        self._ssh('cd MAAPS/server ; sudo pip3 install -r requirements.txt')

    def _ssh(self, cmd, timeout=120):
        ssh_cmd = 'ssh %s@%s %s "%s"' % (self.username, self.ip, SSH_OPTIONS, cmd)
        return self._ssh_exec(ssh_cmd, timeout)

    def _ssh_exec(self,ssh_cmd , timeout):
        fname = tempfile.mktemp()
        fout = open(fname, 'w')
        child = pexpect.spawnu(ssh_cmd, timeout=timeout)  # spawnu for Python 3
        child.expect(['[pP]assword: '])
        child.sendline(self.password)
        child.logfile = fout
        child.expect(pexpect.EOF)
        child.close()
        fout.close()
        fin = open(fname, 'r')
        stdout = fin.read()
        fin.close()
        print(stdout)
        return stdout


class Raspberry(System):
    def install(self, server):
        self._update_raspberry()
        self._install_lcd()
        time.sleep(30) # wait for pi to reboot
        self._install_spi()
        self._install_hardwarepy()
        self._install_autostart_chromium(server)
        self._ssh('sudo reboot')

    def _update_raspberry(self):
        self._ssh('sudo apt-get -y update', timeout=600)
        self._ssh('sudo apt-get -y upgrade', timeout=600)
        self._ssh('sudo apt-get -y remove lxplug-ptbatt pulseaudio cups-browsed', timeout=600)
        self._ssh('''
            cat /boot/config.txt | grep -v avoid_warnings > 1 ; sudo mv 1 /boot/config.txt ;
            echo 'avoid_warnings=1' | sudo tee -a  /boot/config.txt ;
        ''')
        self._ssh('''
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v 'xset s ' > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ;
            echo 'export DISPLAY=:0;xset s 180' | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;
        ''')

    def _install_lcd(self):
        self._ssh('cd /tmp/ && git clone https://github.com/waveshare/LCD-show.git;')
        self._ssh('cd /tmp/LCD-show/ && chmod +x LCD35-show && sudo ./LCD35-show %s;' % self.lcd_rotation)

    def _install_spi(self):
        self._ssh('''
            cat /boot/config.txt | grep -v MAAPS > 1 ; sudo mv 1 /boot/config.txt ;
            echo 'dtoverlay=spi1-1cs,cs0_pin=16 # bcm pin 16, pcb pin 36, MAAPS' | sudo tee -a  /boot/config.txt ;
        ''')

    def _install_hardwarepy(self):
        self._git_download()
        self._ssh('''
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v hardware.py > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ;
            echo 'python3 /home/%s/MAAPS/client/hardware.py' | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;
        ''' % self.username)

    def _install_autostart_chromium(self, server):
        self._ssh('''
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v chromium-browser > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ;
            echo "chromium-browser --disable-restore-session-state --kiosk '%s:8001/%s/%s'" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;
        ''' % (server.ip, self.type, self.token.replace(";","\;")))


class Server(System):
    stunnel_conf = '''
    pid=
    cert = /etc/stunnel/stunnel.pem
    sslVersion = SSLv3
    [https]
    accept=443
    connect=8001
    TIMEOUTclose=1
    sslVersion = all
    options = NO_SSLv2
    '''
    def __init__(self, type, ip, mac_address, username, password):
        super().__init__(type, ip, mac_address, username, password, None, "")

    def install(self):
        self._install_stunnel()
        self._install_server()
        self._ssh('sudo reboot')

    def _install_stunnel(self):
        open("/tmp/stunnel_conf","w").write(Server.stunnel_conf)
        self._ssh_exec('scp %s /tmp/stunnel_conf %s@%s:/tmp/stunnel.conf' % (SSH_OPTIONS, self.username, self.ip), 120)
        self._ssh('sudo apt-get install stunnel')
        self._ssh('''
            cd /etc/stunnel/;
            sudo rm stunnel.key stunnel.cert stunnel.pem ;
            openssl genrsa 2048 |sudo tee -a stunnel.key ; 
            sudo openssl req -new -x509 -nodes -sha1 -days 365 -key stunnel.key  -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.example.com"|sudo tee -a  stunnel.cert ;   
            sudo cat stunnel.key stunnel.cert |sudo tee -a stunnel.pem ;     
            sudo mv /tmp/stunnel.conf /etc/stunnel/stunnel.conf ; 
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v stunnel > /tmp/1 ; sudo mv /tmp/1 /etc/xdg/lxsession/LXDE-pi/autostart ; 
            echo "nohup sudo stunnel4 /etc/stunnel/stunnel.conf" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;  
        ''')

    def _install_server(self):
        self._git_download()
        self._ssh('''
            cd  /home/%s/MAAPS/server/ ; 
            python3 manage.py migrate ; 
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v manage.py > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ; 
            echo "python3 /home/%s/MAAPS/server/manage.py runserver 0.0.0.0:8001" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;  
        ''' % (self.username, self.username))

    def backup(self):
        date_time = datetime.now().strftime("%m.%d.%Y_%H:%M:%S")
        destination = "backups/%s/" % date_time
        os.system("mkdir -p '%s'" % destination)
        ssh_cmd = 'scp -r %s %s@%s:/home/%s/MAAPS/server/media/ %s' % (SSH_OPTIONS, self.username, self.ip, self.username ,destination )
        self._ssh_exec(ssh_cmd, 120)
        ssh_cmd = 'scp %s %s@%s:/home/%s/MAAPS/server/db.sqlite3 %s' % (SSH_OPTIONS, self.username, self.ip, self.username, destination )
        self._ssh_exec(ssh_cmd, 120)
        print("Backup done to '%s'" % destination)

    def restore(self,source_dir):
        self._ssh('ps ax|grep -i runserver|cut -d? -f 1 |cut -dp -f1|xargs kill', 120)
        time.sleep(1)
        ssh_cmd = 'scp %s -r %s/media/ %s@%s:/home/%s/MAAPS/server/ ' % (SSH_OPTIONS, source_dir, self.username, self.ip, self.username )
        self._ssh_exec(ssh_cmd, 120)
        ssh_cmd = 'scp %s %s/db.sqlite3 %s@%s:/home/%s/MAAPS/server/' % (SSH_OPTIONS, source_dir, self.username, self.ip, self.username )
        self._ssh_exec(ssh_cmd, 120)
        print("Restore done from '%s', rebooting" % source_dir)
        self._ssh('sudo reboot')


class POS(Raspberry):
    pass


class Machine(Raspberry):
    pass

class SiteSetup():
    def __init__(self):
        self.server = None
        self.poss = []
        self.machines = []
        self._read_data()

    def scan_network(self, network):
        import scapy.all as scapy
        partialip = ".".join(network.split(".")[0:-1])
        for i in range(0, 256):
            curr_ip = partialip + "." + str(i)
            arp_request = scapy.ARP(pdst=curr_ip)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = scapy.srp(arp_request_broadcast, timeout=0.3, verbose=False)[0]
            for element in answered_list:
                ip = element[1].psrc
                mac = element[1].hwsrc
                status = ""
                if mac.startswith("dc:a6:32"):
                    status = "THIS IS A PI"
                print(ip + "\t\t" + mac + "\t" + status)
                break

    def _read_data(self):
        for l in open("devices.csv","r").read().split("\n")[1:]:
            l = l.strip()
            if l == "":continue
            type, ip, mac_address, username, password, lcd_rotation, token = [p.strip() for p in l.split(",")]
            if type == "server":
                if self.server is not None: raise Exception("Only one server is allowed")
                self.server = Server(type, ip, mac_address, username, password)
            elif type == "pos":
                self.poss.append(POS(type, ip, mac_address, username, password, lcd_rotation, token))
            elif type == "machine":
                self.machines.append(Machine(type, ip, mac_address, username, password, lcd_rotation, token))

help = '''
    setup.py
    setup.py configcard <dir> # enable ssh and wlan on SD card mounted to <dir>
    setup.py search <network>  # search /24 (256 ips) in <network> for raspberry PIs
    setup.py serversetup  # install/upgrade server
    setup.py backup  # backup server
    setup.py restore <source>  # restore server from source folder backup
    setup.py install <ip | all> # install/upgrade raspberry pi machine or PointOfSale
'''

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n    Error: Missing Option\n%s" % help)
        exit(1)

    option = sys.argv[1]

    siteSetup = SiteSetup()

    if option == "configcard":
        if len(sys.argv) < 3:
            print("\n    Error: Missing target directory\n%s" % help)
            exit(1)
        directory = sys.argv[2]
        open(os.path.join(directory, "wpa_supplicant.conf" ), "w").write(open("wpa_supplicant.conf","r").read())
        open(os.path.join(directory, "ssh"), "w").write('')
        print("Card configured")

    elif option == "scan":
        if len(sys.argv) < 3:
            print("\n    Error: Missing target network to scan\n%s" % help)
            exit(1)
        siteSetup.scan_network(sys.argv[2])

    elif option == "install":
        if len(sys.argv) < 3:
            print("\n    Error: Missing target ip or all\n%s" % help)
            exit(1)
        target = sys.argv[2]
        for machine in siteSetup.machines:
            if machine.ip == target or target == "all":
                machine.install(siteSetup.server)
        for pos in siteSetup.poss:
            if pos.ip == target or target == "all":
                pos.install(siteSetup.server)

    elif option == "serversetup":
        siteSetup.server.install()

    elif option == "backup":
        siteSetup.server.backup()

    elif option == "restore":
        if len(sys.argv) < 3:
            print("\n    Error: Missing source folder\n%s" % help)
            exit(1)
        siteSetup.server.restore(sys.argv[2])

    else:
        print("unknown option '%s'" % sys.argv[1])

