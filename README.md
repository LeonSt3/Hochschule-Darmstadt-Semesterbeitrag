# Hochschule Darmstadt — Verlauf der Semesterbeiträge

![Semesterbeitrag](data/semester_plot.png)

## Kurzbeschreibung
- Scraper für die Semesterbeiträge der Hochschule Darmstadt.
- Speichert:
  - `data/history.json` — Zeitreihe
  - `data/semester_plot.png` — generierte Visualisierung

## Funfacts:

### Funfact 1:

Im Sommersemester 2008 war der Semesterbeitrag auf der Website kurzzeitig niedriger \(**697,50 €**\).
Vermutlich wurde auf der Website zunächst nur der Semestertitel aktualisiert, der Betrag aber noch nicht angepasst.

- Sommersemester 2008: **697,50 €**
  https://web.archive.org/web/20071210160236/http://www.h-da.de/studium/information-und-beratung/semesterbeitrag/index.htm
- Sommersemester 2008 später : **709,50 €**  
  https://web.archive.org/web/20080303161704/http://www.h-da.de/studium/information-und-beratung/semesterbeitrag/index.htm

### Funfact 2:
Langzeitstudienbeiträge in Wintersemester 2007/2008 und Sommersemester 2008:

Studierende, die erstmals oder erneut Langzeitstudienbeiträge zahlen mussten, zahlten zusätzlich zum Semesterbeitrag von
209,50 € einen Betrag von 500 €, 700 € oder 900 €.

### Funfact 3:
Ab dem Sommersemester 2010 wurde die Säumnisgebühr von 15 € auf 30 € erhöht.

### Funfact 4:

Für das Sommersemester 2011 gibt es widersprüchliche Angaben: In der älteren PDF (und im Website\-Archiv) werden *
*238,50 €** genannt, in einer neueren PDF\-Version **231,00 €**.
Für die Zeitreihe verwenden wir **238,50 €**, da dieser Betrag sowohl im Website\-Archiv als auch in der älteren PDF
erscheint (vermutlich handelt es sich bei **231,00 €** um einen Übertragungsfehler).
Quelle
\(Webarchiv\): https://web.archive.org/web/20110122093155/http://www.h-da.de/studium/information-und-beratung/semesterbeitrag/index.htm

## Hinweise:

- Die Grafik wird automatisch durch die Pipeline aktuell gehalten; ältere Aufteilungen des Semesterbeitrags stammen aus
  archive.org.
- Nach gemeldeten fehlerhaften Einträgen wurden Validierungs-Tests ergänzt.
- Teile dieses Repos wurden mit KI-gestützten Tools erstellt.
- Gerne Issues oder Pull Requests einreichen
