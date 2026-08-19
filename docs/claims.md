# MAAPS - System Claims & Feature Specification

Dieses Dokument bietet eine vollständige und strukturierte Übersicht aller Spezifikationen und Verhaltensgarantien (**Claims**), die das **MAAPS** (*Machine Access And Payments System*) bereitstellt. Es dient als Grundlage für die automatisierte Testabdeckung und Qualitätssicherung.

---

## 1. Authentifizierung & Token-Architektur

- **Claim 1.1: Eindeutiges Token-Format**
  - RFID-Tokens sind in der Datenbank eindeutig strukturiert:
    - Benutzertokens: `U:<username>;<uuid>`
    - Maschinentokens: `M:<machinename>;<uuid>`
  - Das System unterscheidet strikt zwischen Benutzer- und Maschinenspeicherkarten.

- **Claim 1.2: Schreibberechtigung für Tokens (`can_write`)**
  - Jedes `Token`-Objekt besitzt ein Flag `can_write`.
  - Nur Tokens mit `can_write=True` dürfen am POS-Terminal oder Webif zum Beschreiben neuer RFID-Karten verwendet werden.

- **Claim 1.3: Automatische Token-Zuordnung**
  - Bei der Neuanlage eines Benutzers (sowohl Admin-Anlage als auch Selbstregistrierung) wird automatisch ein verknüpftes `Token` im Format `U:<username>;<uuid>` mit `can_write=True` erzeugt.

---

## 2. Öffentliche Registrierung & Benutzerkonto

- **Claim 2.1: Öffentliches Registrierungsformular (`/register`, `/webif/user/register`)**
  - Erfordert Name (`first_name`, `last_name`), E-Mail (eindeutig), Adresse (`street`, `postalcode`, `city`) und optional Firmenname sowie Profilbild (`profile_picture`).
  - Erzeugt automatisch ein Django `User`-Objekt mit eindeutigem Benutzernamen (`firstname.lastname` oder `firstname.lastname2` bei Namensgleichheit).

- **Claim 2.2: Automatische Signalverarbeitung**
  - Ein `post_save`-Signal auf das `User`-Modell erstellt automatisch das zugehörige `Profile` sowie ein initiales `Token`.

- **Claim 2.3: Admin-Sicherheitsgrenze bei Selbstregistrierung**
  - Das öffentliche Registrierungsformular erlaubt *keine* Auswahl von Maschinenberechtigungen (`allowed_machines`) und *keine* Einstellung von Abrechnungsflags (`commercial_account`, `monthly_payment`). Neue Konten verbleiben im Standard-Prepaid-Tarif bis zur manuellen Admin-Freigabe.

---

## 3. Maschinen-Kiosk-Interface (`/machine/`)

- **Claim 3.1: Maschinenauswahl & Statusanzeige (`/machine/M:<machine_token>`)**
  - Das Display an einer Maschine zeigt bei Aufruf den aktuellen Zustand: frei, besetzt oder gesperrt.

- **Claim 3.2: Benutzer-Login an Maschine (`/machine/login_user/...`)**
  - Beim Einloggen eines Nutzers per RFID-Token an einer freien Maschine wird das Relais eingeschaltet (`GET /relay/all/on` am Hardware-Daemon).
  - Es wird eine neue `MachineSession` erzeugt.

- **Claim 3.3: Tutor-Einweisungspflicht (`tutor_required`)**
  - Benötigt eine Maschine Einweisungen (`tutor_required_count > 0` oder `tutor_required_once_after_month`), prüft das System die bisherigen Sitzungen des Nutzers.
  - Reichen die bisherigen Sitzungen nicht aus, wechselt die Oberfläche in den Tutor-Modus. Die Freischaltung erfolgt erst, wenn ein berechtigter Tutor seine RFID-Karte scannt.

- **Claim 3.4: Bezahlung & Guthabenprüfung (`payment_required`)**
  - Bei kostenpflichtigen Maschinenprüfungen für Prepaid-Nutzer ohne Ausreichend Guthaben/Moni-Guthaben fordert das System eine Guthabenaufladung oder Drittzahler-Bestätigung an (`other_user_pays`).

- **Claim 3.5: Verbrauchsmaterial-Abrechnung (`pay_material`)**
  - Am Ende einer Sitzung kann optional verbrauchtes Material (z. B. Filament, Holz) erfasst werden, was eine `MaterialPayment`-Transaktion auslöst.

- **Claim 3.6: Maschinen-Bewertung (`rate_machine`)**
  - Beim Logout kann der Zustand/die Sauberkeit der Maschine auf einer Skala (1–5) bewertet und in der `MachineSession` gespeichert werden.

- **Claim 3.7: Automatischer Logout (`auto_logout`)**
  - Inaktive Sitzungen oder abgelaufene Zeittimer werden automatisch beendet, woraufhin das Relais abgeschaltet wird (`GET /relay/all/off`).

---

## 4. Point of Sale Terminal (`/pos/`)

- **Claim 4.1: Mitarbeiter- & Kunden-Authentifizierung**
  - Das POS-Terminal erfordert für administrative Aktionen einen Staff-Login (`login_staff`) per Mitarbeiter-RFID-Karte.
  - Kunden melden sich an (`login_user`), um Guthaben einzusehen oder aufzuladen.

- **Claim 4.2: Guthabeneinzahlung (`deposit`)**
  - Über `/pos/deposit/` kann der Mitarbeiter Bargeld oder Guthaben für das Konto eines Mitglieds buchen (`PrepaidDepositPayment`).
  - Das Guthaben im `Profile` des Nutzers erhöht sich umgehend.

- **Claim 4.3: RFID-Karten beschreiben (`write_card`)**
  - Ein Mitarbeiter mit Schreibrecht (`can_write=True`) kann neue RFID-Tokens auf unbeschriebene Karten übertragen (`GET /rfid/write/...` am Hardware-Daemon).

- **Claim 4.4: POS-Information & Abrechnung (`info`, `payment`)**
  - Zeigt Kontoinformationen, offene Beträge und Historie des Kunden an und ermöglicht die Barbezahlung offener Posten.

---

## 5. Web-Interface (`/webif/`)

- **Claim 5.1: Dashboard (`/webif/dashboard`)**
  - Zeigt eine Übersicht aller aktuell aktiven Maschinensitzungen und im Space anwesenden Mitglieder (Space Access Tracking).

- **Claim 5.2: Benutzerverwaltung (`/webif/user/list`, `show`, `create`, `update`, `delete`)**
  - Admins können Mitglieder anlegen, bearbeiten, löschen, Guthaben anpassen und spezifische Maschinenberechtigungen (`allowed_machines`) zuweisen.

- **Claim 5.3: Mitgliedsverträge (`/webif/contract`, `show_contract`)**
  - Generiert und verwaltet Verträge für Mitglieder inklusive SEPA-Lastschriftmandaten.

- **Claim 5.4: Manuelles Beenden von Sitzungen (`/webif/session/end/<id>`)**
  - Bietet Admins die Möglichkeit, hängengebliebene oder vergessene Maschinensitzungen aus der Ferne zu beenden.

- **Claim 5.5: Preisliste & AGB (`/webif/prices`, `/webif/agb`)**
  - Stellt Mitgliedern die aktuellen Maschinen-Tarife und Raumnutzungsbedingungen bereit.

---

## 6. Abrechnungs- & Rechnungs-Engine (Invoicing)

- **Claim 6.1: Erfassung gebührenpflichtiger Vorgänge**
  - Folgende Aktionen erzeugen Zahlungsdatensätze:
    - `MachineSessionPayment` (Maschinennutzung nach Zeit/Sockelbetrag)
    - `MaterialPayment` (Materialverbrauch)
    - `SpaceRentPayment` (Raummiete)
    - `PrepaidDepositPayment` (Einzahlungen)

- **Claim 6.2: Rechnungsgenerierung (`/webif/invoice/create`, `list_createable`)**
  - Das System aggregiert alle abrechenbaren, noch nicht fakturierten Zahlungen eines Nutzers zu einer `Invoice`.
  - Berücksichtigt Steuer/MwSt-Regeln für kommerzielle Accounts (`commercial_account`) und Mitglieder-Tarife (`monthly_payment`).

- **Claim 6.3: Rechnungsanzeige & PDF-Ansicht (`/webif/invoice/show/<id>`)**
  - Rendert detaillierte Rechnungsübersichten mit Einzelpositionen, Fälligkeitsdatum (`due`) und Gesamtbetrag (`total`).

---

## 7. Raumzugangs-Tracking (Space Access Tracking)

- **Claim 7.1: Betreten des Spaces (`spaceaccesstracking`)**
  - Das Einloggen an einem POS- oder Zugangs-Terminal erstellt einen `SpaceAccessTracking`-Eintrag mit Startzeitpunkt.

- **Claim 7.2: Verlassen des Spaces (`/webif/spaceaccesstracking/end/<id>`)**
  - Bucht den Auslogg-Zeitpunkt und schließt den Aufenthalt ab.

---

## 8. REST-API (`/api/`)

- **Claim 8.1: API-Machine-Login (`/api/login/M:<machine_token>/<user_token>`)**
  - Erlaubt die direkte, statlose oder externe Initiierung einer Maschinensitzung via HTTP REST.
  - Prüft Gültigkeit der Tokens, Berechtigungen und Tutor-Status.

- **Claim 8.2: API-Machine-Logout (`/api/logout/M:<machine_token>/<user_token>`)**
  - Beendet die Sitzung für das angegebene Maschinen-/Nutzer-Paar und schaltet das Relais ab.

---

## 9. Management Commands

- **Claim 9.1: Monatliche Raummiete (`create_monthly_spacerentpayments`)**
  - Erzeugt automatisch wiederkehrende `SpaceRentPayment`-Einträge für Nutzer mit aktiven Monatsvereinbarungen.

- **Claim 9.2: Historische Rechnungsaufbereitung (`create_old_invoices`)**
  - Konvertiert abgerechnete Alt-Transaktionen in strukturierte `Invoice`-Objekte.

---

## 10. Hardware-Daemon (`client/hardware.py`)

- **Claim 10.1: Bottle.py Micro-Service & Endpunkte**
  - Stellt HTTP-Endpunkte auf Port 8080 bereit:
    - `GET /rfid/read/`: Liest RFID-Tags.
    - `GET /rfid/write/<value>`: Beschreibt RFID-Tags.
    - `GET /relay/<names>/<value>`: Schaltet Relais 1, 2, 3 oder `all` (`on`/`off`).

- **Claim 10.2: Automatischer Fallback in den Dummy-Modus**
  - Wenn `RPi.GPIO` oder `mfrc522` nicht auf dem Betriebssystem installiert sind (z. B. auf macOS/Linux Dev-Systemen), schaltet der Hardware-Daemon nahtlos in den simulierten Dummy-Modus.
