# Basis-Image: Schlankes Python 3.11
FROM python:3.11-slim

# Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Arbeitsverzeichnis
WORKDIR /app

# System-Abhängigkeiten installieren
# Wir benötigen zlib1g-dev und libjpeg-dev für Pillow (Bildbearbeitung)
# build-essential wird für manche Python-Kompilierungen benötigt
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libjpeg-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Python Abhängigkeiten installieren
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Projektcode kopieren
COPY . /app/

# Entrypoint Skript kopieren und ausführbar machen
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Port freigeben
EXPOSE 8000

# Start-Befehl via Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]