# QR Code Design Studio 🎨

Ein leistungsstarker, Django-basierter QR-Code Generator mit Live-Vorschau, Design-Optionen (Frames, Logos, Farben) und Export-Funktion. Entwickelt für den Einsatz in Docker-Umgebungen (z.B. mit Traefik).

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## ✨ Features

* **Live Vorschau:** Sieh Änderungen (Farbe, Text, Form) in Echtzeit via HTMX.
* **Vielseitige Typen:** * 🌐 Webseite (URL)
    * 📡 WLAN Zugang (automatische Einwahl)
    * 👤 vCard (Digitale Visitenkarte)
    * 📝 Freitext
* **Design Studio:**
    * **Styles:** Wähle zwischen Punkten, Quadraten, abgerundeten Ecken oder Streifen.
    * **Frames:** Polaroid-Look, Smartphone-Rahmen oder schlichte Ränder.
    * **Farben:** Freie Wahl für Vorder- und Hintergrund sowie Text.
* **Branding:**
    * Integrierte Logos (WhatsApp, WiFi, etc.) oder eigener Upload.
    * Text unter dem QR Code mit Custom Fonts (.ttf Support).
* **High Quality Export:** Download als hochauflösendes JPEG.

## 🚀 Installation & Start

### A. Mit Docker (Empfohlen)

Das Projekt ist für den Einsatz mit Docker Compose und Traefik optimiert.

1.  **Repository klonen:**
    ```bash
    git clone [https://github.com/dein-user/qr-gen.git](https://github.com/dein-user/qr-gen.git)
    cd qr-gen
    ```

2.  **Environment Setup:**
    Erstelle eine `.env` Datei im Hauptverzeichnis:
    ```bash
    DEBUG=0
    SECRET_KEY=dein-sehr-geheimer-key-123
    DJANGO_ALLOWED_HOSTS=qr.deinedomain.com,localhost
    ```

3.  **Starten:**
    ```bash
    docker-compose up -d --build
    ```
    Der Service ist nun (je nach Traefik-Config) unter deiner Domain oder `localhost:8009` erreichbar.

### B. Lokale Entwicklung

1.  **Voraussetzungen:** Python 3.10+ installiert.
2.  **Setup:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Migrationen & Start:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

## 📂 Ordnerstruktur & Assets

Damit Logos und Schriftarten funktionieren, erwartet das Projekt folgende Struktur für statische Dateien:

```text
qr_gen_app/static/qr_gen_app/assets/
├── fonts/          # Hier .ttf Dateien ablegen (z.B. arial.ttf)
├── whatsapp.png    # Preset Icons für Logos
├── wifi.png
└── favicon.png     # Browser Icon