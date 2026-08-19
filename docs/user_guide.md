# MAAPS - Benutzerhandbuch (User Guide)

MAAPS (**Machine Access And Payments System**) ist das Verwaltungssystem für den Makerhafen Makerspace. Es steuert den Zugang zu Maschinen, verwaltet Guthaben/Abrechnungen und dient als Kassen- und Mitgliederverwaltungssystem.

---

## Inhaltsverzeichnis

1. [Übersicht & Funktionsweise](#1-übersicht--funktionsweise)
2. [Anmeldung & Benutzerkonto](#2-anmeldung--benutzerkonto)
3. [Maschinenfreischaltung (Machine Access)](#3-maschinenfreischaltung-machine-access)
4. [Point of Sale (POS Terminal)](#4-point-of-sale-pos-terminal)
5. [Web-Interface (Webif)](#5-web-interface-webif)
6. [Abrechnung & Tarife](#6-abrechnung--tarife)
7. [Häufig gestellte Fragen (FAQ)](#7-häufig-gestellte-fragen-faq)

---

## 1. Übersicht & Funktionsweise

MAAPS verwendet **RFID-Karten** (bzw. Chips) zur Identifikation von Personen und Maschinen.
- Jedes Mitglied erhält eine zugewiesene RFID-Karte mit einem eindeutigen Token.
- An jeder gesteuerten Maschine befindet sich ein Raspberry Pi Terminal mit Touchscreen und RFID-Leser.
- Nach dem Einloggen per Karte wird das Relais der Maschine aktiviert (Stromfreigabe).

---

## 2. Anmeldung & Benutzerkonto

### Erstmaliges Einrichten / Erste Karte erhalten
1. **Selbstregistrierung**: Du kannst dich selbstständig über die öffentliche Registrierungsseite (`/register`) mit deinen Daten (Name, E-Mail, Anschrift, optional Foto) anmelden.
2. **Freischaltung durch Admin**: Ein Admin schaltet dein Konto frei, weist dir gewünschte Maschinenberechtigungen zu und händigt dir deine beschriebene RFID-Karte aus.
3. Ab sofort kannst du dich an POS-Terminals und Maschinen mit dieser Karte authentifizieren.

### Tarife und Kontotypen
Dein Konto kann verschiedene Eigenschaften aufweisen:
- **Mitglied (Monthly Payment)**: Ermäßigte oder kostenfreie Nutzung bestimmter Maschinen.
- **Tagesgast (Default)**: Abrechnung pro Nutzung/Stunde nach Standardtarif.
- **Kommerzieller Account**: Nutzung für gewerbliche Zwecke (inkl. MwSt-Ausweis).
- **Rabattierter Account**: z. B. für Jugendliche unter 16 Jahren.
- **Prepaid / Guthaben**: Einzahlungen auf dein internes Makerhafen-Guthabenkonto.

---

## 3. Maschinenfreischaltung (Machine Access)

### Schritt-für-Schritt: Maschine starten
1. Gehe zum Display der gewünschten Maschine.
2. Halte deine **RFID-Karte** an den Lesebereich.
3. Das System prüft deine Einweisungen und deine Berechtigung:
   - **Grüner Bildschirm / Freigabe**: Die Maschine/das Relais schaltet sich ein.
   - **Tutor erforderlich**: Wenn du die Maschine noch nicht ausreichend oft genutzt hast oder eine Auffrischung brauchst, fordert das System eine Bestätigung durch einen Tutor/Einweiser an. Der Tutor muss kurz seine RFID-Karte auflegen.
   - **Guthaben unzureichend**: Falls die Maschine kostenpflichtig ist und kein ausreichendes Guthaben vorhanden ist, wirst du aufgefordert, Guthaben aufzuladen oder eine abweichende Zahlungsart zu wählen.
4. Nach erfolgreicher Freischaltung läuft der Timer und die Maschine ist betriebsbereit.

### Maschinen-Sitzung beenden
- Halte deine Karte erneut an den Leser oder drücke auf dem Touchscreen auf **Logout/Sitzung beenden**.
- Falls gefordert, bewerte die Sauberkeit des Arbeitsplatzes.
- Gib ggf. verbrauchtes Material an.
- Das Relais schaltet die Maschine ab.

---

## 4. Point of Sale (POS Terminal)

Das POS-Terminal befindet sich zentral im Makerspace und dient folgenden Aufgaben:

- **Guthaben aufladen**: Bargeldeinzahlung oder Überweisungsvermerk auf das Prepaid-Konto.
- **Materialien bezahlen**: Kauf von Verbrauchsmaterialien (z. B. Filament, Holz, Platinchen).
- **RFID-Karten beschreiben**: Anlernen neuer Karten für Mitglieder.
- **Kontostand & Historie einsehen**: Prüfen des eigenen Guthabens und vergangener Nutzungssitzungen.

---

## 5. Web-Interface (Webif)

Über das Web-Interface (`/webif/`) haben Mitglieder und Admins Zugriff auf Verwaltungsfunktionen:

- **Dashboard**: Übersicht aller aktiven Sitzungen und Raumaufenthalte.
- **Benutzerverwaltung**: Profil bearbeiten, Adressdaten pflegen, Kontaktdaten aktualisieren.
- **Verträge & SEPA/PayPal**: Ausfüllen und Verwalten von Mitgliedsverträgen und Zahlungsvereinbarungen.
- **Rechnungen & Quittungen**: Einsicht und Download von Abrechnungen für Maschinennutzung und Materialkäufe.
- **Preisliste**: Übersicht der aktuellen Nutzungspreise für alle Geräte im Space.

---

## 6. Abrechnung & Tarife

MAAPS berechnet Gebühren transparent auf Basis von:
- **Nutzungsgebühr (Price per usage)**: Einmaliger Sockelbetrag pro Sitzung.
- **Zeitgebühr (Price per hour)**: Minuten/stundengenaue Abrechnung während der Maschinennutzung.
- **Materialkosten**: Erfassung von verbrauchtem Material im Rahmen der Sitzung.

Abrechnungsarten:
- **Prepaid**: Direkte Verrechnung mit dem aufgeladenen Nutzerguthaben.
- **Postpaid / Rechnung**: Monatliche Sammelabrechnung per E-Mail/PDF.

---

## 7. Häufig gestellte Fragen (FAQ)

#### F: Meine Karte wird am Maschinenterinal nicht erkannt. Was tun?
**A:** Prüfe, ob die Karte beschädigt ist. Wenn das Terminal gar nicht reagiert, wende dich an einen Admin. Eventuell muss dein Token neu auf die Karte geschrieben werden (`/pos/write_card`).

#### F: Die Maschine schaltet nicht ein, obwohl ich angemeldet bin.
**A:** Prüfe, ob eine Einweisung/Tutor erforderlich ist oder ob dein Guthaben im Minus ist. Ein Admin kann den Status im Webif einsehen.

#### F: Kann ich meine Sitzung aus der Ferne beenden?
**A:** Ja, im Webif unter Dashboard / Aktive Sitzungen kann eine offene Sitzung manuell beendet werden (`/webif/session/end/<id>`).
