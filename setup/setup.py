import os
import tempfile
import pexpect
import time
# git clone https://github.com/makerhafen/MAAPS.git
# git pull
# pip3 install -r requirements.py
# python3 manage.py migrate


class Raspberry():
    def __init__(self, type, ip, username, password, lcd_rotation, token):
        self.type = type
        self.ip = ip
        self.username = username
        self.password = password
        self.lcd_rotation = lcd_rotation
        self.token = token

    def ping(self):
        print("### PING %s %s" % (self.type, self.ip))
        os.system("ping -c 2 -t 2 -q -Q %s" % self.ip)

    def _install(self ):
        self._ssh('python3 /home/pi/hardware.py install_lcd %s' % self.lcd_rotation)
        self._ssh('python3 /home/pi/hardware.py install 192.168.43.105 pos' )

    def _git_download(self):
        self._ssh('''
        git clone https://github.com/makerhafen/MAAPS.git ; 
        cd MAAPS ; git pull ; 
        cd client ; sudo pip3 install -r requirements.py ; cd ..
        cd server ; sudo pip3 install -r requirements.py
        ''')

    def _scp(self, source, destination, timeout=30):
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        ssh_cmd = 'scp %s %s %s@%s:%s' % (options, source, self.username, self.ip,destination )
        print(ssh_cmd)
        return self.__ssh(ssh_cmd, timeout)

    def _ssh(self, cmd, timeout=30):
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        ssh_cmd = 'ssh %s@%s %s "%s"' % (self.username, self.ip, options, cmd)
        print(ssh_cmd)
        return self.__ssh(ssh_cmd, timeout)

    def __ssh(self,ssh_cmd , timeout):
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
        if 0 != child.exitstatus:
            raise Exception(stdout)
        return stdout

class ServerSetup(Raspberry):
    pass
class PosSetup(Raspberry):
    pass
class MachineSetup(Raspberry):
    def install(self, server):
        self._git_download()
        self._ssh('sudo python3 /home/pi/MAAPS/client/hardware.py install_lcd %s' % self.lcd_rotation)
        time.sleep(10)
        self._ssh('sudo python3 /home/pi/MAAPS/client/hardware.py install %s:8001 machine %s' % server.ip, self.token)
        self._ssh('sudo reboot')
        time.sleep(10)


def read_data():
    lines = open("setup.csv","r").read().split("\n")[1:]
    servers = []
    poss = []
    machines = []
    for l in lines:
        l = l.strip()
        if l == "":continue
        parts = [p.strip() for p in l.split(",")]
        type, ip, username, password, lcd_rotation, token = parts
        if type == "server":
            servers.append( ServerSetup(type, ip, username, password, lcd_rotation, token))
        elif type == "pos":
            poss.append(PosSetup(type, ip, username, password, lcd_rotation, token))
        elif type == "machine":
            machines.append(MachineSetup(type, ip, username, password, lcd_rotation, token))

    return servers, poss, machines

'''
setup.py
setup.py show  # show known devices

'''
servers, poss, machines = read_data()
for machine in machines:
    machine.install(servers[0])

for client in read_data():
    print(client)
    #print(client.install)
    #print(client.ping())
    #print(client.copy_hardwarepy())
    #print(client.install())