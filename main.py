import os
import json
import re
import matplotlib.pyplot as plt
import itertools
from datetime import datetime

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_PATH = os.path.join(OUT_DIR, "history.json")
PNG_PATH = os.path.join(OUT_DIR, "semester_plot.png")

EPSILON = 1e-9


def safe_num(v):
    if v is None:
        return None
    try:
        return float(v)
    except:
        # falls string wie "103,00 €"
        m = re.search(r"[-\d\.,]+", str(v))
        if not m:
            return None
        num = m.group(0).strip().replace(".", "").replace(",", ".")
        try:
            return float(num)
        except:
            return None


# --- Normalisierung von Komponenten-Namen ---
def normalize_name(name: str) -> str:
    if not name:
        return name
    n = name.strip().lower()
    # Synonyme für Semesterticket / RMV zusammenfassen
    if "rmv" in n or "öpnv" in n or "semesterticket" in n or "bundesweit" in n:
        return "Semesterticket"
    # Leihfahrradsystem / Call a bike vereinheitlichen
    if "call a bike" in n or "leihfahrradsystem" in n:
        return "Leihfahrradsystem"
    # Verwaltungskostenbeitrag mit/ohne * vereinheitlichen
    if "verwaltungskosten" in n:
        return "Verwaltungskostenbeitrag"
    # Studierendenschaft / Studierendenwerksbeitrag etc.
    if "studierendenwerks" in n:
        return "Studierendenwerksbeitrag"
    if "studierendenschaft" in n:
        return "Studierendenschaftsbeitrag"
    if "kulturticket" in n:
        return "Kulturticket"
    # Standard: trim und Title-Case
    return name.strip()


def load_entries():
    entries = []
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except:
            entries = []
    return entries


def build_table(entries):
    # entries: list of parsed results from scraper, newest last
    labels = []
    rows = []
    components_order = []
    # determine a sensible order from the latest entry if present
    if entries:
        latest = entries[-1]
        if latest.get("items"):
            seen = set()
            ordered = []
            for it in latest["items"]:
                nm = it.get("name")
                if not nm:
                    continue
                can = normalize_name(nm)
                if can not in seen:
                    seen.add(can)
                    ordered.append(can)
            components_order = ordered
    # fallback: build union of components
    all_names = set()
    for e in entries:
        name = e.get("semester") or e.get("total") or e.get("fetched_at") or datetime.utcnow().isoformat()
        labels.append(name)
        comp_map = {}
        for it in e.get("items", []):
            n = it.get("name")
            # value extraction and normalization
            v_raw = it.get("value") if "value" in it else it.get("amount")
            v = safe_num(v_raw)
            canonical = normalize_name(n)
            # Falls mehrere Einträge im selben Semester nach Normalisierung zusammenfallen -> aufsummieren
            if v is None:
                # markiere als fehlend, wenn noch kein Wert gesetzt ist
                if canonical not in comp_map:
                    comp_map[canonical] = None
            else:
                prev = comp_map.get(canonical)
                if prev is None:
                    comp_map[canonical] = v
                else:
                    comp_map[canonical] = prev + v
            all_names.add(canonical)
        rows.append({"label": name, "comps": comp_map, "raw": e})
    if not components_order:
        components_order = sorted([n for n in all_names if n], key=lambda x: x.lower())
    return labels, rows, components_order


def totals_and_stacks(labels, rows, components_order):
    stack_values = {c: [] for c in components_order}
    totals = []
    missing_flags = []
    for r in rows:
        comps = r["comps"]  # enthält nur Komponenten, die in diesem Eintrag gelistet wurden
        missing = False
        total = 0.0
        # Für jede Komponente: wenn sie in diesem Eintrag vorhanden ist und einen Wert hat -> addieren.
        # Wenn die Komponente in diesem Eintrag vorhanden ist, aber keinen Wert (None) -> markieren als missing.
        # Wenn die Komponente in diesem Eintrag nicht vorkommt -> als 0.0 behandeln (nicht missing).
        for c in components_order:
            if c in comps:
                v = comps[c]
                if v is None:
                    # explizit vorhanden, aber kein Wert -> fehlend
                    missing = True
                    stack_values[c].append(0.0)
                else:
                    total += v
                    stack_values[c].append(v)
            else:
                # Komponente nicht gelistet -> historisch nicht vorhanden, also 0
                stack_values[c].append(0.0)
        totals.append(total if not missing else None)
        missing_flags.append(missing)
    return totals, stack_values, missing_flags


# NEU: Formatierung von Euro-Werten ohne überflüssige Nullen
def format_euro(v):
    if v is None:
        return "n.a."
    try:
        # Wenn Wert praktisch ganzzahlig ist, ohne Nachkommastellen anzeigen
        if abs(v - round(v)) < EPSILON:
            return f"{int(round(v))} €"
        # Sonst mit zwei Nachkommastellen
        return f"{v:.2f} €"
    except Exception:
        return f"{v} €"


def plot_and_save(labels, totals, stack_values, components_order, missing_flags):
    if not labels:
        print("Keine Daten zum Plotten gefunden.")
        return
    x = list(range(len(labels)))
    known_totals = [t for t in totals if t is not None and t > 0]
    max_known = max(known_totals) if known_totals else 1.0

    plt.figure(figsize=(max(10, len(labels) * 0.45), 6))
    ax = plt.gca()
    colors = plt.get_cmap("tab20").colors
    color_cycle = itertools.cycle(colors)

    bottom = [0] * len(labels)
    for comp in components_order:
        vals = stack_values[comp]
        color = next(color_cycle)
        ax.bar(x, vals, bottom=bottom, color=color, label=comp, edgecolor='white', width=0.7)
        bottom = [bottom[i] + vals[i] for i in range(len(bottom))]

    # ensure y-limits leave space for annotations
    top_value = max(max(bottom) if bottom else 0.0, max_known)
    ax.set_ylim(0, top_value * 1.12)

    # annotate totals or placeholder (mit lesbarem Hintergrund)
    for i, lbl in enumerate(labels):
        if totals[i] is not None:
            ax.text(
                i,
                totals[i] + top_value * 0.02,
                format_euro(totals[i]),
                ha="center",
                va="bottom",
                fontsize=8,
                zorder=11,
                bbox={"facecolor": "white", "alpha": 0.75, "pad": 1, "edgecolor": "none"},
            )
        else:
            placeholder_height = top_value * 0.03
            ax.bar(i, placeholder_height, color="#eeeeee", edgecolor="#999999", hatch='//', width=0.7, zorder=5)
            ax.text(
                i,
                placeholder_height + top_value * 0.02,
                "n.a.",
                ha="center",
                va="bottom",
                fontsize=8,
                color="#333333",
                zorder=11,
                bbox={"facecolor": "white", "alpha": 0.75, "pad": 1, "edgecolor": "none"},
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("Euro")
    ax.set_title("Zusammensetzung Semesterbeitrag (gestapelt)")
    ax.legend(title="Komponenten", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    plt.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    plt.savefig(PNG_PATH, dpi=150)
    plt.close()
    print("Plot gespeichert:", PNG_PATH)


def main():
    entries = load_entries()
    labels, rows, components_order = build_table(entries)
    totals, stack_values, missing_flags = totals_and_stacks(labels, rows, components_order)
    plot_and_save(labels, totals, stack_values, components_order, missing_flags)


if __name__ == "__main__":
    main()
