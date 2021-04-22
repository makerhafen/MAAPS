import os
import tempfile
import pexpect
import time

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

    def _git_download(self):
        self._ssh('''
        git clone https://github.com/makerhafen/MAAPS.git ; 
        cd MAAPS ; git pull ; 
        cd client ; sudo pip3 install -r requirements.py ; cd ..
        cd server ; sudo pip3 install -r requirements.py
        ''')

    def _install_hardware(self, server):
        self._git_download()

        self._ssh('sudo python3 /home/pi/MAAPS/client/hardware.py install_lcd %s' % self.lcd_rotation)

        time.sleep(20)

        self._ssh('sudo python3 /home/pi/MAAPS/client/hardware.py install %s:8001 machine %s' % (server.ip, self.token))
        self._ssh('sudo reboot')

    def _scp(self, source, destination, timeout=120):
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        ssh_cmd = 'scp %s %s %s@%s:%s' % (options, source, self.username, self.ip,destination )
        print(ssh_cmd)
        return self._ssh_exec(ssh_cmd, timeout)

    def _ssh(self, cmd, timeout=120):
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        ssh_cmd = 'ssh %s@%s %s "%s"' % (self.username, self.ip, options, cmd)
        print(ssh_cmd)
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

class ServerSetup(Raspberry):
    '''
    openssl genrsa 2048 |sudo tee -a stunnel.key
    sudo openssl req -new -x509 -nodes -sha1 -days 365 -key stunnel.key |sudo tee -a  stunnel.cert
    sudo cat stunnel.key stunnel.cert |sudo tee -a  stunnel.pem
    '''

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

    # self signed dummy cert
    stunnel_pem = '''
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEAqwoH8kjNrWa3gNT2sikGulWuZa3HA13B+w3WRjFmweOSuq9/
L30sBTvUiWScExXCE4vn3Kc0ksXGaaQd4TfAC1qrGcGjEyx1K8n6HqHbvS0qRUiI
X+x03JlI9c3KgBH8C/siYHiHKMaICbA9ONMGGheMInmVsbU7yA13bqZprFMrUPX0
f++fb3zXHPoCYwLwbOcufS5gDOiWv79IbvKwtBPKXPtWdtvogJ68cPKmw+UbUh37
demxGXNZlfVzyudJTeOO1OKUFeB/QoNBVaK6jeWn17uUiPs25ryg3l00k4tj+FJb
vbhwsVVHrHcq+eTpNLAlcEtak8QA88E6gO0hqwIDAQABAoIBAQCjn0IA1wLj2nq7
5X9m6naENUlT/g1/u+bBa/hLSCE8ZJ/OterfHEjLbPQix7vDSjJSjqmt3cseidMI
5raq6LFwazl5t1NxGTuyO1NqkH7tF9LzWrMTyNn22zD/7PHG2O2c7I9zaHosWNh1
JEM9JCsXNOWbaWL6ER1ygOd7U/mNnqVkwRa95X+XVoJmjHvewlBh9Q6aJMSce2Z0
Fu4Z+UGnXGFOJzli6OZAP3A6gExQx+e10nQZWreQAiyiSfX75FjgxleXTfPI+ZGW
/5SRNmhgTrdmfMNissi+7KMIvI2JAdmMicopaRG/e8KKIe2VrWwDpmOHdaFuUZp/
u0TMcdz5AoGBAOA/5lAZFta4290F82s6ZBk1VW3WIN0bqGGWhnZdUkmNGnUvs/EZ
6RH8oQ07yxA6y99Y8TvDvb9CvdVnFnks5rXifBfdaZO5vANOrbfiCGDpWQDNt4PY
ZQXCVeNfxDlXc30ExRKUhx5+I/NCMGsrlce5aTY+Hh7VV+3o3Bg9zbO3AoGBAMNB
enqKS/RZCCuN6ABE2v+wcb3Ytj2wdBkWLAbmAfphPORBl0hhKllmWhH/j0h96u6j
M3p0+PYgk4hnPfiIABMWFWK3FN4EE9BjTWcdxNFYPsLsQaQqxw31Ot2h4O5wiYVL
ZuAzK9QWEqkIcZFFRVHprbrN50Z7pw3B6GC7sMmtAoGAW9bPpA4iZF3g7Wv6fPe0
9v34trrzSpqBIzZaay9c+/Jl24hl0WAjK9KiwqCyUTtDM31hjnBjzWiwBi3p7kaN
VgAjgkKTcoSmk1QtoRlZBReL8+BMQBrnhKxKMIyP+EvwaEsDytA5ZiuS3ZVF7x4y
gVFV3XkjLM2C7VRojyUAkZECgYEAlawSs+5hLMw2rBRaXCJr8YYSmmGNyRoC1Nwf
Iaacq45wO9RfoBcDfIYt0xAgiIQlW4p0wpD56smr7eqeIW43CGpsOEB5WXqsqZgF
VF8IaSUI7yhlZO95qKRr3ErjfkN711amZIQ1O50z7qjPTXlZGuJSzxhZCblto+kZ
NVWKvf0CgYBAQp17Kn53w04FRXO5EHrXsASmdohZF7r3CBNVFF2X8JIx2ySk4KGE
QvATyYz0wGDqqYxZbIxi2Q7cxKYoPQl5dLqMgXGOrX0ev59rJB4rMtq2UQ8IfZjd
d3aNWFXbriwVr8ET+wq8W1r1reZgARMXdt+C3PDq8FP7OV3+XAXTuA==
-----END RSA PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIIDazCCAlOgAwIBAgIUFEHVxDR3b9zbN8pwTAkAcR9SIF0wDQYJKoZIhvcNAQEF
BQAwRTELMAkGA1UEBhMCQVUxEzARBgNVBAgMClNvbWUtU3RhdGUxITAfBgNVBAoM
GEludGVybmV0IFdpZGdpdHMgUHR5IEx0ZDAeFw0yMTA0MjIyMzI0MjhaFw0yMjA0
MjIyMzI0MjhaMEUxCzAJBgNVBAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEw
HwYDVQQKDBhJbnRlcm5ldCBXaWRnaXRzIFB0eSBMdGQwggEiMA0GCSqGSIb3DQEB
AQUAA4IBDwAwggEKAoIBAQCrCgfySM2tZreA1PayKQa6Va5lrccDXcH7DdZGMWbB
45K6r38vfSwFO9SJZJwTFcITi+fcpzSSxcZppB3hN8ALWqsZwaMTLHUryfoeodu9
LSpFSIhf7HTcmUj1zcqAEfwL+yJgeIcoxogJsD040wYaF4wieZWxtTvIDXdupmms
UytQ9fR/759vfNcc+gJjAvBs5y59LmAM6Ja/v0hu8rC0E8pc+1Z22+iAnrxw8qbD
5RtSHft16bEZc1mV9XPK50lN447U4pQV4H9Cg0FVorqN5afXu5SI+zbmvKDeXTST
i2P4Ulu9uHCxVUesdyr55Ok0sCVwS1qTxADzwTqA7SGrAgMBAAGjUzBRMB0GA1Ud
DgQWBBRI9I9BS5uXeNODHGLIGB1kiyOkTDAfBgNVHSMEGDAWgBRI9I9BS5uXeNOD
HGLIGB1kiyOkTDAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBBQUAA4IBAQB7
U0dg5SxCSabMPGJf9K5xcE4KbYfd+EI/7ZKi8vs/Vy3xEGsUBrSNsjVGCu9DhavD
TZJg8XP8LmlaCqsub5OTrvPWHLxJh7D2OuVumyz1LgXKxoYbG1qUPhX3xP9/nnoi
K9t0F5dmMEYIkLuxJ5I9Vgx0VR5f3N1n7WwOtXEVTY1Fu6HN5chFZr5+A4FysgRr
X1KGnYvDq5qJLKgZgdodo/CXx+yjOmw+ubppP+OA6lA/ZWysGzKN8ebwIvJca/dE
n0dxqd1kD55tippq4uMcM9jEvlNV3Dy7qucKLSE1i4cLQuFl1wBJOKfLj3LMCHYg
7b43XjK82nnXXjZvl/9D
-----END CERTIFICATE-----
    '''

    def install(self):
        self._git_download()
        self._ssh('''
           sudo apt-get install stunnel
        ''')
        open("/tmp/stunnel_pem","w").write(ServerSetup.stunnel_pem)
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        ssh_cmd = 'scp %s /tmp/stunnel_pem %s@%s:/tmp/stunnel.pem' % (options, self.username, self.ip)
        self._ssh_exec(ssh_cmd, 120)
        open("/tmp/stunnel_conf","w").write(ServerSetup.stunnel_conf)
        ssh_cmd = 'scp %s /tmp/stunnel_conf %s@%s:/tmp/stunnel.conf' % (options, self.username, self.ip)
        self._ssh_exec(ssh_cmd, 120)

        self._ssh('''
            sudo mv /tmp/stunnel.conf /etc/stunnel/stunnel.conf
            sudo mv /tmp/stunnel.pem /etc/stunnel/stunnel.pem
            cd  /home/pi/MAAPS/server/ ; 
            python3 manage.py migrate ; 
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v manage.py > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ; 
            cat /etc/xdg/lxsession/LXDE-pi/autostart | grep -v stunnel > 1 ; sudo mv 1 /etc/xdg/lxsession/LXDE-pi/autostart ; 
            echo "python3 /home/pi/MAAPS/server/manage.py runserver 0.0.0.0:8001" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;  
            echo "nohup sudo stunnel4 /etc/stunnel/stunnel.conf" | sudo tee -a /etc/xdg/lxsession/LXDE-pi/autostart ;  
        ''')

    def backup(self):
        destination = "backups/%s/" % int(time.time())
        os.system("mkdir -p '%s'" % destination)
        options = '-q -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -oPubkeyAuthentication=no'
        ssh_cmd = 'scp -r %s %s@%s:/home/pi/MAAPS/server/media/ %s' % (options, self.username, self.ip,destination )
        self._ssh_exec(ssh_cmd, 120)
        ssh_cmd = 'scp %s %s@%s:/home/pi/MAAPS/server/db.sqlite3 %s' % (options, self.username, self.ip,destination )
        self._ssh_exec(ssh_cmd, 120)

class PosSetup(Raspberry):
    def install(self, server):
        self._install_hardware(server)

class MachineSetup(Raspberry):
    def install(self, server):
        self._install_hardware(server)


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
for server in servers:
    server.install()
#for machine in machines:
#    machine.install(servers[0])
#for pos in poss:
#    pos.install(servers[0])
#for server in servers:
#    server.backup()
