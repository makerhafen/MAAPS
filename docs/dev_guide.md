# MAAPS - Entwicklerdokumentation (Developer Guide)

Willkommen zur Entwicklerdokumentation von **MAAPS** (Machine Access And Payments System). Diese Dokumentation richtet sich an Softwareentwickler, Systemadministratoren und Hardware-Hacker, die das System warten, erweitern oder neu bereitstellen möchten.

---

## Inhaltsverzeichnis

1. [Systemarchitektur](#1-systemarchitektur)
2. [Tech Stack](#2-tech-stack)
3. [Ordnerstruktur](#3-ordnerstruktur)
4. [Datenmodelle (Django Models)](#4-datenmodelle-django-models)
5. [Client-Hardware & Hardware-Daemon (`client/hardware.py`)](#5-client-hardware--hardware-daemon-clienthardwarepy)
6. [Server & Webif / POS / API Route-Struktur](#6-server--webif--pos--api-route-struktur)
7. [Installation & Setup-Automatisierung (`setup.py`)](#7-installation--setup-automatisierung-setuppy)
8. [Sicherheitsarchitektur & bekannte Schwachstellen](#8-sicherheitsarchitektur--bekannte-schwachstellen)
9. [Entwicklung & Lokales Testen](#9-entwicklung--lokales-testen)

---

## 1. Systemarchitektur

MAAPS basiert auf einer **Client-Server-Architektur**:

```
+-------------------------------------------------------+
|                    MAAPS Server                       |
|  - Django Web Application                             |
|  - SQLite Database (db.sqlite3)                       |
|  - Views: POS, Machine-Flow, Webif, REST-like API     |
+-------------------------------------------------------+
       ^                                    ^
       | HTTP/HTTPS                         | HTTP/HTTPS
       v                                    v
+----------------------------+   +----------------------------+
|   Raspberry Pi (POS)       |   | Raspberry Pi (Machine)     |
| - Bottle.py Hardware-Daemon|   | - Bottle.py Hardware-Daemon|
| - RFID RC522 Reader        |   | - RFID RC522 Reader        |
| - 3.5" Touch Display       |   | - 3-Relais-Board (GPIO)    |
| - Chromium Kiosk           |   | - Chromium Kiosk           |
+----------------------------+   +----------------------------+
```

---

## 2. Tech Stack

### Server Stack
- **Sprache**: Python 3
- **Web-Framework**: Django (Version 2/3 kompatibel)
- **Datenbank**: SQLite3 (`db.sqlite3`)
- **Formulare & UI**: `django-crispy-forms`, `crispy-bootstrap4`, Bootstrap 4
- **Bildverarbeitung**: `django-resized` (Pillow)
- **Hilfsbibliotheken**: `unidecode`

### Client / Hardware Stack
- **Hardware**: Raspberry Pi (B+ / 2 / 3 / 4)
- **Display**: Waveshare 3.5" Touch Screen (SPI / LCD35)
- **RFID-Reader**: MFRC522 (SPI Bus 1, Device 0)
- **Relais**: 3-Kanal Relais-Board via GPIO (Pins 26, 13, 6)
- **Local Micro-Server**: Bottle.py (auf Port 8080)
- **Automatisierung/Provisionierung**: `pexpect`, `scapy` (Arp-Scan)

---

## 3. Ordnerstruktur

```
MAAPS/
├── client/
│   ├── hardware.py         # Bottle.py Service & RFID/Relay Ansteuerung
│   └── requirements.txt    # Client Python-Pakete (bottle, RPi.GPIO, gpiozero, mfrc522)
├── hardware/               # Gehäuse-Dateien (CAD / Fusion 360, Bilder)
├── server/
│   ├── db.sqlite3          # SQLite-Datenbank
│   ├── manage.py           # Django Management CLI
│   ├── requirements.txt    # Server Python-Pakete
│   └── maaps/
│       ├── admin.py        # Django Admin Registrierungen
│       ├── models.py       # Sämtliche ORM-Modelle
│       ├── settings.py     # Django Konfiguration
│       ├── urls.py         # URL Routing
│       ├── views/          # Modularisierte Views (api, machine, pos, webif, functions)
│       └── templates/      # HTML-Templates (Bootstrap 4)
├── setup.py                # Automatisierte Pi-Provisionierung & System-Management
└── docs/                   # Projektdokumentation
```

---

## 4. Datenmodelle (Django Models)

Die zentralen Datenstrukturen befinden sich in `server/maaps/models.py`:

- **`Profile`**: Erweitert `django.contrib.auth.models.User` (OneToOne). Verwaltet Zahlungstypen, Guthaben (`prepaid_deposit`), Tarifflags (`commercial_account`, `discount_account`, `monthly_payment`) und Adressdaten.
- **`Token`**: RFID-Schlüsselkennung. Format: `U:<username>;<uuid>` für Nutzer bzw. `M:<machinename>;<uuid>` für Maschinen.
- **`Machine`**: Repräsentiert ein Gerät/Werkzeug. Enthält Verweise auf Preise (`Price`), Tutor-Regeln (`tutor_required_count`, `tutor_required_once_after_month`), aktuelle Session und freigegebene Nutzer (`allowed_users`).
- **`MachineSession`**: Aufzeichnung einer konkreten Nutzung (Start, Ende, Nutzer, Tutor, Autologout-Zeitpunkt, Rating).
- **`Price`**: Preisstaffel (Default, Members, Discount, Commercial).
- **Zahlungsmodelle**:
  - `MachineSessionPayment` (Maschinennutzung)
  - `MaterialPayment` (Materialkäufe)
  - `PrepaidDepositPayment` (Guthabeneinzahlungen)
  - `SpaceRentPayment` (Tages-/Monatsmiete)
- **`Transaction` & `Invoice`**: Buchhaltungs- und Rechnungsverwaltung.

---

## 5. Client-Hardware & Hardware-Daemon (`client/hardware.py`)

Auf jedem Raspberry Pi läuft ein lokaler Bottle.py HTTP-Server auf Port 8080:

- **Endpunkte**:
  - `GET /rfid/read/`: Liest den aktuellen RFID-Tag bargeldlos ab (`<token_id>\t<text>`).
  - `GET /rfid/write/<value>`: Schreibt einen Token-String auf einen MFRC522 Tag.
  - `GET /relay/<names>/<value>`: Schaltet Relais 1, 2, 3 oder `all` auf `on` oder `off`.
- **Display-Steuerung**: Schaltet nach Relais-Aktivierung den Screenblanking-Modus um (`xset s off` vs `xset s 180`).
- **Debugging**: Wenn RPi.GPIO/mfrc522 nicht vorhanden sind, schaltet der Code automatisch in den **Dummy-Modus** für Entwicklung auf PC/Mac.

---

## 6. Server & Webif / POS / API Route-Struktur

In `server/maaps/urls.py` definierte Pfadgruppen:

- **`/pos/`**: Point of Sale Interface (Kassenkraft-Anmeldung, Guthaben, Kartenschreiben, Info).
- **`/machine/`**: Kiosk-Oberfläche für Maschinendisplays (`/machine/M:<machine_token>`).
- **`/api/`**: Direkte Schnittstelle zur Maschinensteuerung:
  - `GET /api/login/M:<machine_token>/<user_token>`
  - `GET /api/logout/M:<machine_token>/<user_token>`
- **`/webif/`**: Dashboard, Benutzerverwaltung, Rechnungen, Verträge, Raum-Tracking.
- **`/register` / `/webif/user/register`**: Öffentliche Registrierungsseite (`PublicRegisterForm`) für neue Mitglieder ohne Admin-Einschränkungen/Maschinenfreigaben.

---

## 7. Installation & Setup-Automatisierung (`setup.py`)

Das Skript `setup.py` (im Repository-Stammverzeichnis) dient der automatisierten Bereitstellung, Sicherung und Verwaltung der Pi-Flotte via SSH und Pexpect.

### Deployment-Ordnerstruktur

Standortspezifische Konfigurations- und Sicherungsdateien werden getrennt vom Quellcode in einem eigenen **Site Deployment Folder** aufbewahrt (z. B. `files/MAAPS-Deployment/`):

```
MAAPS-Deployment/
├── devices.csv         # Liste aller Geräte (Server, POS, Machines) mit IP, MAC, SSH-Zugangsdaten, Token
├── wpa_supplicant.conf # WLAN-Konfigurationsdatei für neue Raspberry Pis
├── secret_key.txt      # Django SECRET_KEY für den Server (wird bei Erstinstallation automatisch generiert)
└── backups/            # Automatisch erstellte Datenbank- und Media-Backups (z.B. YYYY.MM.DD_HH:MM:SS/)
```

#### Aufbau der `devices.csv`
Die CSV-Datei definiert die Netzwerk- und Zugangsdaten der Geräte:
```csv
system_type, ip, mac_address, username, password, lcd_rotation, token
server, 192.168.1.100, dc:a6:32:00:00:01, pi, secretpass, 0,
pos, 192.168.1.101, dc:a6:32:00:00:02, pi, secretpass, 90, POS_01
machine, 192.168.1.102, dc:a6:32:00:00:03, pi, secretpass, 90, LASER_01
```

---

### Befehlszeilenübersicht (CLI Usage)

Jeder Aufruf von `setup.py` erwartet den Pfad zum Deployment-Ordner als ersten Parameter:

```bash
python3 setup.py <site_deployment_folder> <befehl> [optionen]
```

#### 1. Gerätekonfiguration anzeigen
Zeigt die im Deployment-Ordner hinterlegte `devices.csv` an:
```bash
python3 setup.py /path/to/MAAPS-Deployment show
```

#### 2. Server installieren / aktualisieren
Klont/aktualisiert das Repository auf dem Zielserver, überträgt/generiert `secret_key.txt` aus dem Deployment-Ordner, installiert Python-Abhängigkeiten, richtet `stunnel` für HTTPS auf Port 443 ein, führt `manage.py migrate` aus und richtet den Autostart via `maaps_start.sh` ein:
```bash
python3 setup.py /path/to/MAAPS-Deployment serversetup
```

#### 3. Client-Geräte (POS & Maschinen) installieren / aktualisieren
Installiert Systemupdates, Waveshare LCD35-Displaytreiber, SPI-Overlays, Hardware-Daemon Autostart und Chromium Kiosk-Modus für ein bestimmtes Gerät oder alle Geräte (`all`):
```bash
python3 setup.py /path/to/MAAPS-Deployment install 192.168.1.102
python3 setup.py /path/to/MAAPS-Deployment install all
```

#### 4. Backup erstellen
Erstellt einen zeitgestempelten Ordner unter `<site_deployment_folder>/backups/YYYY.MM.DD_HH:MM:SS/` und sichert `db.sqlite3` sowie den Ordner `media/` via SSH/SCP vom Server:
```bash
python3 setup.py /path/to/MAAPS-Deployment backup
```

#### 5. Backup wiederherstellen
Stoppt den laufenden Server-Prozess, überträgt `db.sqlite3` und `media/` aus dem angegebenen Backup-Quellordner auf den Server und startet diesen neu:
```bash
python3 setup.py /path/to/MAAPS-Deployment restore /path/to/MAAPS-Deployment/backups/2026.08.19_12:00:00
```

#### 6. SD-Karte für neuen Raspberry Pi vorbereiten
Kopiert `wpa_supplicant.conf` aus dem Deployment-Ordner auf die gemountete SD-Karte und aktiviert SSH (durch Anlegen der Datei `ssh`):
```bash
python3 setup.py /path/to/MAAPS-Deployment configcard /Volumes/boot
```

#### 7. Netzwerkanalyse (IP / MAC Scan)
Scannt ein Subnetz per ARP-Scan nach aktiven Raspberry Pis und vergleicht gefundene MAC-Adressen mit `devices.csv` (erfordert `sudo`):
```bash
sudo python3 setup.py /path/to/MAAPS-Deployment scan 192.168.1.0
```

---

## 8. Sicherheitsarchitektur & bekannte Schwachstellen

> ⚠️ **Sicherheitshinweise für die Modernisierung / Produktion**:

1. **Hardcoded Secrets**: `SECRET_KEY` in `settings.py` ist im Repository hinterlegt. Für die Produktion zwingend über Umgebungsvariablen (`os.environ`) einlesen!
2. **Debug-Modus**: `DEBUG = True` und `ALLOWED_HOSTS = ["*"]` sind aktiv. Muss in Produktion deaktiviert werden.
3. **HTTP / CORS**: Lokaler Bottle-Server nutzt offenes CORS (`Access-Control-Allow-Origin: *`) ohne TLS/HTTPS.
4. **SSH-Protokolle**: `setup.py` verwendet `StrictHostKeyChecking=no` und Klartext-Passwörter in Skripten.

---

## 9. Entwicklung & Lokales Testen

### Server lokal starten
```bash
cd server
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver 0.0.0.0:8000
```

### Client / Hardware-Daemon lokal simulieren
```bash
cd client
pip3 install -r requirements.txt
python3 hardware.py
```
*(Startet im Dummy-Modus auf `http://127.0.0.1:8080/`)*
