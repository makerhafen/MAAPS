import time
import sys
import os

try:
    from gpiozero import LED
    import RPi.GPIO as GPIO
    from mfrc522 import SimpleMFRC522
    from mfrc522 import MFRC522
except:
    class LED(): # for local debugging without raspberry
        def __init__(self, pin):
            self.pin = pin
            print("dummy relay on PIN %s" % self.pin)
        def on(self): print("dummy relay pin %s ON" % self.pin)
        def off(self): print("dummy relay pin %s OFF" % self.pin)
    class SimpleMFRC522():
        def write(self, value):
            print("dummy rfid write", value)
        def read(self):
            print("dummy rfid read")
            return 23, "test value"
    class GPIO():
        @classmethod
        def cleanup(cls): pass

relay_1 = LED(26) # PIN 37
relay_2 = LED(13)
relay_3 = LED(6)
relay_1.on() # relay board is low active
relay_2.on()
relay_3.on()

def __init__(self, bus, device):
   self.READER = MFRC522(bus=bus, device=device)
SimpleMFRC522.__init__ = __init__
rfid_reader = SimpleMFRC522(bus=1, device=0)

def read_rfid():
    id, text = None, None
    for i in range(5):
        id, text  = rfid_reader.read_no_block()
        if id != None:
            text = text.strip()
            print("successful read", text)
            break
        time.sleep(0.1)
    return id, text

def write_rfid(text):
    id, output = None, None
    for i in range(5):
        id, output  = rfid_reader.write_no_block(text)
        if id != None:
            break
        time.sleep(0.1)
    return id, output

def install(lcd_rotation, host):
    os.system("apt-get update")
    os.system("apt-get upgrade")
    if lcd_rotation != -1:
        os.system("cd /tmp/ && git clone https://github.com/waveshare/LCD-show.git")
        os.system("cd /tmp/LCD-show/ && chmod +x LCD35-show && ./LCD35-show %s" % lcd_rotation)

    os.system("pip3 install spidev mfrc522 bottle")
    configline = 'dtoverlay=spi1-1cs,cs0_pin=16 # bcm pin 16, pcb pin 36'
    content = open("/boot/config.txt","r").read()
    if configline not in content:
        content += "\n%s" % configline
    open("/boot/config.txt", "w").write(content)

    content = open("/etc/xdg/lxsession/LXDE-pi/autostart","r").read()
    configline = 'python3 /home/pi/hardware.py'
    if configline not in content:
        content += "\n%s" % configline
    configline = 'chromium-browser --disable-restore-session-state  --kiosk %s' % host
    if configline not in content:
        content += "\n%s" % configline
    open("/etc/xdg/lxsession/LXDE-pi/autostart","w").write(content)

if len(sys.argv) > 1:
    if sys.argv[1] == "write":
        print("RFID TAG AUFLEGEN")
        print(write_rfid(sys.argv[2]))
    if sys.argv[1] == "read":
        print("RFID TAG AUFLEGEN")
        print(read_rfid())
    if sys.argv[1] == "install":
        lcd_rotation = sys.argv[2] # 0,90,180,270 or -1 to disable lcd install
        host = sys.argv[3] # 0,90,180,270 or -1 to disable lcd install
        install(lcd_rotation,host)
    exit(0)

from bottle import route, run
import bottle
from bottle import response

def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, X-Test'
        if bottle.request.method != 'OPTIONS':
            return fn(*args, **kwargs)
    return _enable_cors

@route('/rfid/read/', method=['OPTIONS', 'GET'])
@enable_cors
def rfid_token():
    id, text = read_rfid()
    if id is None:
        return ""
    return "%s\t%s" % (id, text)

@route('/rfid/write/<value>', method=['OPTIONS', 'GET'])
@enable_cors
def rfid_token(value=""):
    if value != "":
        id, text = write_rfid(value)
        if id is not None:
            return "OK"
    return "Failed"

@route('/write_output/<value>', method=['OPTIONS', 'GET'])
@enable_cors
def write_output(value="000"):
    if len(value) >= 3 and value[2] == "1": relay_3.off()  # relay board is low active
    else: relay_3.on()

    if len(value) >= 2 and value[1] == "1": relay_2.off()
    else: relay_2.on()

    if len(value) >= 1 and value[0] == "1": relay_1.off()
    else: relay_1.on()

    print(value)
    return "OK"

run(host='127.0.0.1', port=8080)