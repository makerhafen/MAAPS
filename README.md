### MAAPS

MAAPS - Machine Access And Payments System

#### Hardware

- Raspberry PI 4
- Raspberry 3.5 inch Touch Display https://www.amazon.de/dp/B07YV5WYM3
- RFID card reader https://www.amazon.de/dp/B074S9FZC5
- Raspberry Pi Relay Board https://www.amazon.de/dp/B01FZ7XLJ4

#### Setup

##### Server
```
python3 manage.py migrate
python3 manage.py createsuperuser 
```
Run Server with
```
python3 manage runserver 0.0.0.0:8000
```
Open a browser, connect to your server on <ip:port>/admin and login with your admin user.
Open the "Tokens" page and remember the token identifier for admin (for example U:admin;4c31a8d19b95a7dfe85c)


##### Raspberry

Copy /raspberry/hardware.py to your raspberry pi /home/pi/hardware.py and run:
```
python3 hardware.py install_lcd <lcd_rotation> 
## pi will reboot at this point
python3 hardware.py install <host_and_port>
```

Set <lcd_rotation> to 0,90,180,270 depending on your needs    
Set <host_and_port> according to your server setup

Create the first admin rfid card with 

```
python3 hardware.py write <token>
```
Set token to the admin token identifier you found on the servers admin page.
 