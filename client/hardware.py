import time
import sys
import os
from bottle import route
import bottle
from bottle import response


RFID_SPI_BUS = 1  # SPI BUS for RFID
RFID_SPI_DEVICE = 0  # SPI device for RFID

RELAY_1_GPIO = 26  # Raspi GPIO for Relay 1
RELAY_2_GPIO = 13  # Raspi GPIO for Relay 2
RELAY_3_GPIO = 6  # Raspi GPIO for Relay 3

##
## RELAY
##
try:
    from gpiozero import LED
    import RPi.GPIO as GPIO
except:
    class LED:  # for local debugging without client
        def __init__(self, pin):
            self.pin = pin
            print("Dummy LED class, Pin %s" % self.pin)

        def on(self):
            print("Dummy LED class, Pin %s, ON" % self.pin)

        def off(self):
            print("Dummy LED class, Pin %s, OFF" % self.pin)


    class GPIO:
        @classmethod
        def cleanup(cls): pass


class RelayBoard:
    class _Relay:
        def __init__(self, name, raspi_gpio, board):
            self.name = name
            self.RASPI_GPIO = raspi_gpio
            self._ledio = LED(raspi_gpio)
            self.board = board
            self.is_active = False

        def enable(self):
            print("%s enable" % self.name)
            self._ledio.off()  # relay board is low active
            self.is_active = True
            self.board.check_screenblank()

        def disable(self):
            print("%s disable" % self.name)
            self._ledio.on()
            self.is_active = False
            self.board.check_screenblank()

    def __init__(self):
        self.relay_1 = self._Relay("Relay 1", RELAY_1_GPIO, self)
        self.relay_2 = self._Relay("Relay 2", RELAY_2_GPIO, self)
        self.relay_3 = self._Relay("Relay 3", RELAY_3_GPIO, self)
        self.relay_1.disable()
        self.relay_2.disable()
        self.relay_3.disable()

    def check_screenblank(self):
        if self.relay_1.is_active is True or self.relay_2.is_active is True or self.relay_3.is_active is True:
            os.system('export DISPLAY=:0;xset s off;xset s -dpms')
        else:
            os.system('export DISPLAY=:0;xset s 180;xset s +dpms')


##
## RFID
##
try:
    from mfrc522 import SimpleMFRC522
    from mfrc522 import MFRC522
except:  # Dummy class for debugging without client
    class SimpleMFRC522:
        def __init__(self, bus, device):
            pass

        @staticmethod
        def write(value):
            print("Dummy RFID write '%s'" % value)
            return 12345, value

        def write_no_block(self, value):
            return self.write(value)

        @staticmethod
        def read():
            print("Dummy RFID read")
            return 54321, "U:admin;4c31a8d19b95a7dfe85c"

        def read_no_block(self):
            return self.read()


    class MFRC522:
        def __init__(self, bus, device): pass


class RFID:
    def __init__(self):
        def simpleMFRC522__init(_self, bus, device):  # monkey patch SimpleMFRC522 to support bus and device parameter
            _self.READER = MFRC522(bus=bus, device=device)

        SimpleMFRC522.__init__ = simpleMFRC522__init
        self.rfid_reader = SimpleMFRC522(bus=RFID_SPI_BUS, device=RFID_SPI_DEVICE)

    def read(self):
        token_id, text = None, None
        for i in range(5):
            token_id, text = self.rfid_reader.read_no_block()
            if token_id is not None:
                text = text.strip()
                print("successful read", text)
                break
            time.sleep(0.1)
        return token_id, text

    def write(self, text):
        token_id, output = None, None
        for i in range(5):
            token_id, output = self.rfid_reader.write_no_block(text)
            if token_id is not None:
                break
            time.sleep(0.1)
        return token_id, output


##
## WEB API
##
def btl_enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers[
            'Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, X-Test'
        if bottle.request.method != 'OPTIONS':
            return fn(*args, **kwargs)

    return _enable_cors


@route('/rfid/read/', method=['OPTIONS', 'GET'])
@btl_enable_cors
def route_rfid_read():
    token_id, text = rfid.read()
    if token_id is None:
        return ""
    return "%s\t%s" % (token_id, text)


@route('/rfid/write/<value>', method=['OPTIONS', 'GET'])
@btl_enable_cors
def route_rfid_write(value=""):
    if value != "":
        token_id, text = rfid.write(value)
        if token_id is not None:
            return "OK"
    return "Failed"


@route('/relay/<names>/<value>', method=['OPTIONS', 'GET'])  # 1,2,3,all   on,off
@btl_enable_cors
def route_relay(names="all", value="off"):
    names = names.split(",")
    relays_to_use = []

    if "1" in names or "all" in names: relays_to_use.append(relayboard.relay_1)
    if "2" in names or "all" in names: relays_to_use.append(relayboard.relay_2)
    if "3" in names or "all" in names: relays_to_use.append(relayboard.relay_3)

    if value == "on":
        [r.enable() for r in relays_to_use]
    elif value == "off":
        [r.disable() for r in relays_to_use]

    print(names, value)
    return "OK"


##
## Commandline
##
if __name__ == "__main__":
    rfid = RFID()

    if len(sys.argv) == 1:
        relayboard = RelayBoard()
        bottle.run(host='127.0.0.1', port=8080)
    else:
        if sys.argv[1] == "write":
            print("RFID TAG AUFLEGEN")
            print(rfid.write(sys.argv[2]))
        elif sys.argv[1] == "read":
            print("RFID TAG AUFLEGEN")
            print(rfid.read())
        else:
            print("Unknown Option '%s'" % sys.argv[1])
