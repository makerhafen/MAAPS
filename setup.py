import os
import tempfile
import pexpect
import time
import sys
import random
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

SSH_OPTIONS = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'

PI_MACS = ["dc:a6:32:", "b8:27:eb", "e4:5f:01"]


class System:
    def __init__(self, system_type, ip, mac_address, username, password, lcd_rotation, token):
        self.system_type = system_type
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

    def _ssh_exec(self, ssh_cmd, timeout):
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

    def reboot(self):
        self._ssh('sudo reboot')
        print("System %s rebooting" % self.ip)


class Raspberry(System):
    def install(self, server):
        self._update_raspberry()
        self._install_lcd()
        time.sleep(30)  # wait for pi to reboot
        self._install_spi()
        self._install_hardwarepy()
        self._install_autostart_chromium(server)
        self._install_wlan_restarter(server)
        self.reboot()

    def _update_raspberry(self):
        self._ssh('echo "deb http://legacy.raspbian.org/raspbian/ buster main contrib non-free rpi" > /tmp/apt', timeout=600)
        self._ssh('sudo mv  /tmp/apt /etc/apt/sources.list', timeout=600)

        self._ssh('sudo apt-get -y update', timeout=600)
        self._ssh('sudo apt-get -y upgrade', timeout=600)
        self._ssh('sudo apt-get -y remove --purge lxplug-ptbatt pulseaudio cups-browsed piwiz ', timeout=600)
        self._ssh('sudo apt-get -y remove --purge wolfram-engine triggerhappy anacron logrotate dphys-swapfile', timeout=600)
        self._ssh('sudo systemctl disable bootlogs', timeout=600)
        self._ssh('sudo systemctl disable console-setup', timeout=600)
        self._ssh('sudo apt-get -y install busybox-syslogd chromium-browser', timeout=600)
        self._ssh('sudo dpkg --purge rsyslog', timeout=600)

        self._ssh('''
            cat /boot/config.txt | grep -v avoid_warnings > 1 ; sudo mv 1 /boot/config.txt ;
            echo 'avoid_warnings=1' | sudo tee -a  /boot/config.txt ;
        ''')
        self._ssh('''
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v 'xset s ' > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ;
            echo 'export DISPLAY=:0;xset s 180;xset s +dpms' | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;
        ''')
        self._ssh('''sudo mkdir /var/log/maaps''', timeout=600)
        self._ssh('''sudo chmod -R 777 /var/log/maaps''', timeout=600)

    def _install_lcd(self):
        self._ssh('sudo rm -rf /tmp/LCD-show/ ; sudo rm -rf /home/pi/LCD-show/ ')
        self._ssh('cd /home/pi/ && git clone https://github.com/waveshare/LCD-show.git;')
        self._ssh('cd /home/pi/LCD-show/ && chmod +x LCD35-show && sudo ./LCD35-show %s;' % self.lcd_rotation)

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
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v chromium-browser | grep -v epiphany > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ; mkdir /home/pi/.epiphany/ ; 
            echo 'chromium-browser --disable-restore-session-state --kiosk %s:8001/%s/%s' | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;
        ''' % (server.ip, self.system_type, self.token.replace(" ", "%20")))

    def _install_wlan_restarter(self, server):
        open("/tmp/wlan_check.sh", "w").write('''
            #!/bin/bash
            /bin/ping -W 2 -c 1 -I 'wlan0' '%s' > /dev/null 2> /dev/null
            if [ $? -ge 1 ] ; then
                /bin/sleep 10
                /bin/ping -W 2 -c 2 -I 'wlan0' '%s' > /dev/null 2> /dev/null
                if [ $? -ge 1 ] ; then
                    /sbin/ifdown 'wlan0'
                    /bin/sleep 10
                    /sbin/ifup --force 'wlan0'
                fi
            fi
            exit 0
        ''' % (server.ip, server.ip))

        self._ssh_exec('scp %s /tmp/wlan_check.sh %s@%s:/tmp/wlan_check.sh' % (SSH_OPTIONS, self.username, self.ip), 120)
        self._ssh('sudo mv /tmp/wlan_check.sh /usr/local/sbin/wlan_check.sh')
        self._ssh('sudo chmod +x /usr/local/sbin/wlan_check.sh')
        self._ssh('''
            cat /etc/crontab | grep -v wlan_check > 1 ; sudo mv 1 /etc/crontab ;
            echo '*/2 * * * * /usr/local/sbin/wlan_check.sh' | sudo tee -a /etc/crontab ;
        ''')


class Server(System):
    def __init__(self, system_type, ip, mac_address, username, password):
        super().__init__(system_type, ip, mac_address, username, password, None, "")

    def install(self, secret_key=""):
        self._install_stunnel()
        self._install_server(secret_key)
        self.reboot()

    def _install_stunnel(self):
        self._ssh('sudo apt-get -y update')
        self._ssh('sudo apt-get -y install stunnel')
        open("/tmp/stunnel_conf", "w").write('''
            pid=
            cert = /etc/stunnel/stunnel.pem
            sslVersion = SSLv3
            debug=2
            syslog=no
            [https]
            accept=443
            connect=8001
            TIMEOUTclose=1
            sslVersion = all
            options = NO_SSLv2
        ''')
        self._ssh_exec('scp %s /tmp/stunnel_conf %s@%s:/tmp/stunnel.conf' % (SSH_OPTIONS, self.username, self.ip), 120)
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

    def _install_server(self, secret_key=""):
        self._git_download()
        if secret_key:
            self._ssh('echo "%s" > /home/%s/MAAPS/server/secret_key.txt' % (secret_key, self.username))

        self._ssh('''
            echo '#!/bin/bash' > /home/%s/maaps_start.sh
            echo 'export SECRET_KEY="%s"' >> /home/%s/maaps_start.sh
            echo 'python3 /home/%s/MAAPS/server/manage.py runserver 0.0.0.0:8001 >> /var/log/maaps/server.log 2>&1' >> /home/%s/maaps_start.sh
            chmod +x /home/%s/maaps_start.sh
        ''' % (self.username, secret_key, self.username, self.username, self.username, self.username))

        self._ssh('''
            cd  /home/%s/MAAPS/server/ ; 
            python3 manage.py migrate ; 
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v manage.py > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ; 
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v maaps_start.sh > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ; 
            echo '/home/%s/maaps_start.sh' | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;
        ''' % (self.username, self.username))

    def backup(self, deployment_folder):
        date_time = datetime.now().strftime("%Y.%m.%d_%H:%M:%S")
        destination = os.path.join(deployment_folder, "backups", date_time)
        print("Creating new backup dir '%s'" % destination)
        os.makedirs(destination, exist_ok=True)

        ssh_cmd = 'scp -r %s %s@%s:/home/%s/MAAPS/server/media/ %s' % (SSH_OPTIONS, self.username, self.ip, self.username, destination)
        print("Backing up media, please wait")
        self._ssh_exec(ssh_cmd, 120)

        ssh_cmd = 'scp %s %s@%s:/home/%s/MAAPS/server/db.sqlite3 %s' % (SSH_OPTIONS, self.username, self.ip, self.username, destination)
        print("Backing up database, please wait")
        self._ssh_exec(ssh_cmd, 120)

        os.system("du -sh '%s'" % destination)
        print("Backup done to '%s'" % destination)

    def restore(self, source_dir):
        self._ssh('ps ax|grep -i runserver|cut -d? -f 1 |cut -dp -f1|xargs kill', 120)
        time.sleep(1)
        ssh_cmd = 'scp %s -r %s/media/ %s@%s:/home/%s/MAAPS/server/ ' % (
            SSH_OPTIONS, source_dir, self.username, self.ip, self.username)
        self._ssh_exec(ssh_cmd, 120)
        ssh_cmd = 'scp %s %s/db.sqlite3 %s@%s:/home/%s/MAAPS/server/' % (
            SSH_OPTIONS, source_dir, self.username, self.ip, self.username)
        self._ssh_exec(ssh_cmd, 120)
        print("Restore done from '%s'" % source_dir)
        self.reboot()


class POS(Raspberry):
    pass


class Machine(Raspberry):
    pass


class SiteSetup:
    def __init__(self, deployment_folder):
        self.deployment_folder = os.path.abspath(deployment_folder)
        if not os.path.isdir(self.deployment_folder):
            raise FileNotFoundError("Deployment-Ordner '%s' existiert nicht" % self.deployment_folder)
        self.server = None
        self.poss = []
        self.machines = []
        self._read_data()
        self._scan_network_data = []
        self._scan_network_ip = ""
        self._scan_network_progress_current = 0
        self._scan_network_progress_target = 0

    def scan_network(self, network):
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]
        partialip = ".".join(network.split(".")[0:-1])
        ips_chunks = [c for c in chunks([partialip + "." + str(i) for i in range(0, 255)], 4)]
        random.shuffle(ips_chunks)

        print("\nScanning %s to %s.255" % (network, partialip))
        self._scan_network_data = []
        self._scan_network_progress_current = 0
        self._scan_network_progress_target = 255
        with ThreadPool(4) as p:
            p.map(self._scan_network, ips_chunks)

        print(" Scan done       ")
        print(" %s IPs active" % len(self._scan_network_data))
        print(" %s unknown Raspberry PI found" % len([x for x in self._scan_network_data if x.find("UNKNOWN PI") != -1]))
        print(" %s MAAPS devices found" % len([x for x in self._scan_network_data if x.find("MAAPS") != -1]))
        print("\nResults:")
        self._scan_network_data.sort(key=lambda item: tuple(int(part) for part in item.split("\t")[0].split('.')))
        for nd in self._scan_network_data:
            print(nd)

    def _scan_network(self, ips):
        import scapy.all as scapy
        for ip in ips:
            arp_request = scapy.ARP(pdst=ip)
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast / arp_request
            answered_list = scapy.srp(arp_request_broadcast, timeout=0.3, verbose=False)[0]
            self._scan_network_progress_current += 1
            print(" Scan: %s%%\r" % round(100 / self._scan_network_progress_target * self._scan_network_progress_current), end="")
            for element in answered_list:
                ip = element[1].psrc.strip()
                mac = element[1].hwsrc.strip()
                status = ""
                for PI_MAC in PI_MACS:
                    if mac.startswith(PI_MAC):
                        status = "THIS IS AN UNKNOWN PI"
                        m = self._get_known_by_mac(mac)
                        if m is not None:
                            status = "MAAPS device: %s" % m.system_type
                            if m.token != "":
                                status += ", Token: %s" % m.token
                self._scan_network_data.append(ip + "\t\t" + mac + "\t" + status)

    def _get_known_by_mac(self, mac):
        if self.server and self.server.mac_address == mac:
            return self.server
        m = [m for m in self.machines if m.mac_address == mac]
        if len(m) > 0:
            return m[0]
        p = [p for p in self.poss if p.mac_address == mac]
        if len(p) > 0:
            return p[0]
        return None

    def _read_data(self):
        devices_file = os.path.join(self.deployment_folder, "devices.csv")
        if not os.path.isfile(devices_file):
            raise FileNotFoundError("devices.csv in Deployment-Ordner '%s' nicht gefunden" % self.deployment_folder)

        lines = open(devices_file, "r").read().split("\n")[1:]
        for l in lines:
            l = l.strip()
            if l == "":
                continue
            system_type, ip, mac_address, username, password, lcd_rotation, token = [p.strip() for p in l.split(",")]
            if system_type == "server":
                if self.server is not None:
                    raise Exception("Only one server is allowed")
                self.server = Server(system_type, ip, mac_address, username, password)
            elif system_type == "pos":
                self.poss.append(POS(system_type, ip, mac_address, username, password, lcd_rotation, token))
            elif system_type == "machine":
                self.machines.append(Machine(system_type, ip, mac_address, username, password, lcd_rotation, token))

    def get_or_create_secret_key(self):
        secret_file = os.path.join(self.deployment_folder, "secret_key.txt")
        if os.path.isfile(secret_file):
            with open(secret_file, "r") as f:
                key = f.read().strip()
                if key:
                    return key
        import secrets
        key = secrets.token_urlsafe(50)
        with open(secret_file, "w") as f:
            f.write(key + "\n")
        print("Ein neuer SECRET_KEY wurde generiert und in '%s' gespeichert." % secret_file)
        return key

    def show(self):
        print("Devices configuration (%s/devices.csv):" % self.deployment_folder)
        devices_file = os.path.join(self.deployment_folder, "devices.csv")
        print(open(devices_file, "r").read())


helptxt = '''
MAAPS Deployment & Management Tool

Verwendung:
    python3 setup.py <site_deployment_folder> <command> [options]
    python3 setup.py help

Befehle:
    show                       Gerätekonfiguration aus devices.csv anzeigen
    serversetup                Server auf Zielsystem installieren/aktualisieren
    install <ip | all>         Raspberry Pi (POS / Machine) installieren/aktualisieren
    backup                     Server-Datenbank & Media in <site_deployment_folder>/backups/ sichern
    restore <source>           Server aus Backup-Ordner <source> wiederherstellen
    configcard <dir>           WLAN (wpa_supplicant.conf) & SSH auf gemounteter SD-Karte (<dir>) einrichten
    scan <network>             Subnetz (z.B. 192.168.1.0) nach Raspberry PIs scanen (erfordert root)
    help                       Diese Hilfe anzeigen

Beispiel:
    python3 setup.py /path/to/MAAPS-Deployment show
    python3 setup.py /path/to/MAAPS-Deployment backup
'''

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ["help", "-h", "--help"]:
        print(helptxt)
        exit(0)

    site_deployment_folder = sys.argv[1]

    if not os.path.isdir(site_deployment_folder):
        print("\n    Fehler: Ungültiger Deployment-Ordner '%s'\n%s" % (site_deployment_folder, helptxt))
        exit(1)

    if len(sys.argv) < 3:
        print("\n    Fehler: Fehlender Befehl für Deployment-Ordner '%s'\n%s" % (site_deployment_folder, helptxt))
        exit(1)

    option = sys.argv[2]

    try:
        siteSetup = SiteSetup(site_deployment_folder)
    except Exception as e:
        print("\n    Fehler beim Laden des Deployment-Ordners: %s\n" % e)
        exit(1)

    if option == "configcard":
        if len(sys.argv) < 4:
            print("\n    Fehler: Fehlendes Zielverzeichnis der SD-Karte\n%s" % helptxt)
            exit(1)
        directory = sys.argv[3]
        wpa_file = os.path.join(siteSetup.deployment_folder, "wpa_supplicant.conf")
        if os.path.isfile(wpa_file):
            open(os.path.join(directory, "wpa_supplicant.conf"), "w").write(open(wpa_file, "r").read())
        else:
            print("Hinweis: wpa_supplicant.conf nicht in '%s' gefunden, erstelle leere Datei." % siteSetup.deployment_folder)
        open(os.path.join(directory, "ssh"), "w").write('')
        print("SD-Karte in '%s' erfolgreich für SSH und WLAN konfiguriert." % directory)

    elif option == "scan":
        if len(sys.argv) < 4:
            print("\n    Fehler: Fehlendes Zielnetzwerk zum Scannen (z.B. 192.168.1.0)\n%s" % helptxt)
            exit(1)
        if os.geteuid() != 0:
            print("\n    Fehler: Netzwerkanalyse erfordert ROOT-Rechte (sudo)\n")
            exit(1)
        siteSetup.scan_network(sys.argv[3])

    elif option == "install":
        if len(sys.argv) < 4:
            print("\n    Fehler: Fehlende Ziel-IP oder 'all'\n%s" % helptxt)
            exit(1)
        target = sys.argv[3]
        for machine in siteSetup.machines:
            if machine.ip == target or target == "all":
                machine.install(siteSetup.server)
        for pos in siteSetup.poss:
            if pos.ip == target or target == "all":
                pos.install(siteSetup.server)

    elif option == "serversetup":
        secret_key = siteSetup.get_or_create_secret_key()
        siteSetup.server.install(secret_key)

    elif option == "backup":
        siteSetup.server.backup(siteSetup.deployment_folder)

    elif option == "show":
        siteSetup.show()

    elif option == "restore":
        if len(sys.argv) < 4:
            print("\n    Fehler: Fehlendes Backup-Quellverzeichnis\n%s" % helptxt)
            exit(1)
        siteSetup.server.restore(sys.argv[3])

    else:
        print("\n    Fehler: Unbekannter Befehl '%s'\n%s" % (option, helptxt))
