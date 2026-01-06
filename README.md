# HDA Semesterbeitrag — Beobachtung

![Semesterbeitrag](data/semester_plot.png)

Kurzbeschreibung
- Dieses Repo scrapt automatisch die Seite der Hochschule Darmstadt (Semesterbeitrag) und speichert:
  - data/latest.json — zuletzt gefundene Werte
  - data/<semester-slug>.json — pro Semester
  - data/history.json — Zeitreihe
  - data/semester_plot.png — generierte Visualisierung

CI / GitHub Actions
- Workflow: .github/workflows/scrape.yml
- Läuft täglich (cron) und kann manuell gestartet werden.
- Bei Änderung werden data/*.json und data/*.png committet und in den Repo gepusht.

Lokal ausführen
1. Python 3.11, Abhängigkeiten installieren:
   pip install -r requirements.txt
2. Scraper:
   python scraper/scrape_semesterbeitrag.py
3. Grafik erzeugen:
   python main.py
4. Ergebnisse: siehe `data/`

Hinweis zur Darstellung
- Das README zeigt die im Repo gespeicherte Bilddatei `data/semester_plot.png`. Die GitHub Actions aktualisieren diese Bilddatei — das README zeigt automatisch die neueste Version nach Push.

Lizenz & Haftung
- Nur ein persönliches Projekt; bitte respektiere die Nutzungsbedingungen der Zielseite beim Scrapen.

