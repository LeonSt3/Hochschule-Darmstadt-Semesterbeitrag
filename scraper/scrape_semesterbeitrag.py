import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re
import sys
import unicodedata

URL = "https://h-da.de/studium/studienorganisation/semesterbeitrag"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LATEST_PATH = os.path.join(OUT_DIR, "latest.json")
HISTORY_PATH = os.path.join(OUT_DIR, "history.json")

def clean_amount(text):
    if not text:
        return None
    t = text.strip()
    t = t.replace("\xa0", " ")
    return t

def amount_to_number(text):
    if not text:
        return None
    # akzeptiert z.B. "103,00 €" oder " 2,71 €"
    m = re.search(r"[-\d\.,]+", text)
    if not m:
        return None
    num = m.group(0).strip().replace(".", "").replace(",", ".")
    try:
        return float(num)
    except:
        return None

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    result = {"source": URL, "fetched_at": datetime.utcnow().isoformat() + "Z", "semester": None, "total": None, "total_value": None, "items": []}

    # Suche nach Überschrift "Betrag" und direkt folgendes h3 (z.B. "Sommersemester 2026: 383 €")
    h2 = soup.find(lambda tag: tag.name == "h2" and "Betrag" in tag.get_text())
    if h2:
        h3 = h2.find_next_sibling("h3")
        if h3:
            txt = h3.get_text(strip=True)
            result["total"] = clean_amount(txt)
            # Extrahiere semester und nummer falls möglich
            m = re.match(r"(.+?):\s*(.+)", txt)
            if m:
                result["semester"] = m.group(1).strip()
                result["total_value"] = amount_to_number(m.group(2))
            else:
                result["semester"] = txt

    # Tabelle: Zusammensetzung
    # Suche nach table im nächsten container
    table = None
    if h2:
        table = h2.find_next("table")
    if not table:
        table = soup.find("table", {"class": "ce-table"})
    if table:
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) >= 2:
                name = tds[0].get_text(" ", strip=True)
                val = tds[1].get_text(" ", strip=True)
                name = name.replace("\xa0", " ").strip()
                val = clean_amount(val)
                if name and name.lower() != "zusammensetzung":
                    item = {"name": name, "amount": val, "value": amount_to_number(val)}
                    result["items"].append(item)

    return result

def slugify(text):
    if not text:
        return "unknown"
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text

def save(result):
    os.makedirs(OUT_DIR, exist_ok=True)

    def normalize(obj):
        # entferne volatile Felder bevor verglichen wird
        n = dict(obj)
        n.pop("fetched_at", None)
        n.pop("source", None)
        return n

    changed_any = False

    # latest: nur schreiben, wenn sich relevanter Inhalt geändert hat
    existing_latest = None
    if os.path.exists(LATEST_PATH):
        try:
            with open(LATEST_PATH, "r", encoding="utf-8") as f:
                existing_latest = json.load(f)
        except:
            existing_latest = None

    if existing_latest is None or normalize(existing_latest) != normalize(result):
        # schreibe latest nur wenn relevant unterschiedlich
        try:
            with open(LATEST_PATH, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            changed_any = True
        except Exception as e:
            print("Fehler beim Schreiben von latest.json:", e, file=sys.stderr)

    # per-semester file (slugified) — nur schreiben, wenn nicht vorhanden oder unterschiedlich
    sem_label = result.get("semester") or result.get("total") or datetime.utcnow().strftime("%Y-%m-%d")
    sem_slug = slugify(sem_label)
    per_sem_path = os.path.join(OUT_DIR, f"{sem_slug}.json")
    write_per_sem = True
    if os.path.exists(per_sem_path):
        try:
            with open(per_sem_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if normalize(existing) == normalize(result):
                write_per_sem = False
        except:
            write_per_sem = True
    if write_per_sem:
        try:
            with open(per_sem_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            changed_any = True
        except Exception as e:
            print("Fehler beim Schreiben der Semesterdatei:", e, file=sys.stderr)

    # history: append only if different from last entry (wie vorher)
    history = []
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            history = []
    last = history[-1] if history else None
    if not last or normalize(last) != normalize(result):
        history.append(result)
        try:
            with open(HISTORY_PATH, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            changed_any = True
        except Exception as e:
            print("Fehler beim Schreiben von history.json:", e, file=sys.stderr)

    return changed_any

def main():
    try:
        resp = requests.get(URL, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print("Fehler beim Laden der Seite:", e, file=sys.stderr)
        sys.exit(2)
    parsed = parse(resp.text)
    changed = save(parsed)
    print("Gescannte Daten:", parsed.get("semester"), parsed.get("total"))
    if changed:
        print("Daten haben sich geändert — Dateien aktualisiert.")
        # Rückgabewert 0 auch bei Änderung (workflow entscheidet über Commit)
        sys.exit(0)
    else:
        print("Keine Änderung.")
        sys.exit(0)

if __name__ == "__main__":
    main()

