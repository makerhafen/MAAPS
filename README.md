## MAAPS

MAAPS - Machine Access And Payments System

### Hardware

- Raspberry PI 4
- Raspberry 3.5 inch Touch Display https://www.amazon.de/dp/B07YV5WYM3
- RFID card reader https://www.amazon.de/dp/B074S9FZC5
- Raspberry Pi Relay Board https://www.amazon.de/dp/B01FZ7XLJ4
- Buchsenleiste extra hoch https://www.amazon.de/dp/B07YDKX8SR/
- Jumper Wire Female-Female 10cm https://www.amazon.de/dp/B07GJLCGG8/

| Pinheader  | Raspi    | Function | Hardware    | Hint |
|------------|----------|----------|-------------|------|
| Pin 1      | 3.3V     | 3.3V     | RFID Pin 1  | Löten, Pin belegt von LCD |
| Pin 34     | GND      | GND      | RFID Pin 3  |      |
| Pin 35     | GPIO 19  | MISO     | RFID Pin 5  |      |
| Pin 36     | GPIO 16  | CS0      | RFID Pin 8  |      |
| Pin 38     | GPIO 20  | MOSI     | RFID Pin 6  |      |
| Pin 40     | GPIO 21  | SCLK     | RFID Pin 7  |      |
|            |          |          |             |      |
| Pin 31     | GPIO  6  | Relais 3 | Relais CH3  |      |
| Pin 33     | GPIO 13  | Relais 2 | Relais CH2  |      |
| Pin 37     | GPIO 26  | Relais 1 | Relais CH1  | Jumper auf Relais board |


### Server
```
python3 manage.py migrate
python3 manage.py createsuperuser 
```
Run Server with
```
python3 manage runserver 0.0.0.0:8000
```
Open a browser, connect to your server on {ip:port}/admin and login with your admin user.


### Raspberry

Copy /raspberry/hardware.py to your raspberry pi /home/pi/hardware.py.

##### Install LCD driver
Set {lcd_rotation} to 0,90,180,270 depending on your needs, your pi will reboot after this command
``` 
sudo python3 hardware.py install_lcd {lcd_rotation} 
```

##### Write first card
Open the admin page {ip:port}/admin, open the "Tokens" page and get the token identifier for admin (for example U:admin;4c31a8d19b95a7dfe85c)
```
python3 hardware.py write "YOUR_TOKEN_HERE"
```

##### Setup Point Of Sale   
```
sudo python3 hardware.py install {host_and_port} pos
```
Set {host_and_port} according to your server setup  

##### Setup Machine
Add Machine in admin webinterface, get machine token.

```
sudo python3 hardware.py install {host_and_port} machine {token}
```
Set {host_and_port} according to your server setup  
Set {token} to token of machine
