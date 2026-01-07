# HDA Semesterbeitrag — Beobachtung

![Semesterbeitrag](data/semester_plot.png)

Kurzbeschreibung
- Dieses Repo scrapt automatisch die Seite der Hochschule Darmstadt (Semesterbeitrag) und speichert:
  - data/history.json — Zeitreihe (wichtigste Datei)
  - data/latest.json — Komfort (wird nur aktualisiert, wenn sich Inhalt ändert)
  - data/<semester-slug>.json — pro Semester (Komfort, wird nur angelegt/überschrieben bei Änderung)
  - data/semester_plot.png — generierte Visualisierung

Wichtiges Verhalten
- Pipeline läuft monatlich (cron) und ist manuell triggerbar.
- Commit im Repo erfolgt nur, wenn sich tatsächliche Daten geändert haben (history/ per-semester/ latest werden nur bei relevantem Unterschied geschrieben). Dadurch werden unnötige Commits vermieden.

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
