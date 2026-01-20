import json
import os
import re
from datetime import datetime

import matplotlib.pyplot as plt

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_PATH = os.path.join(OUT_DIR, "history.json")
PNG_PATH = os.path.join(OUT_DIR, "semester_plot.png")

EPSILON = 1e-9

# zusätzlicher Parameter: Abstandsfaktor zwischen Balken (1.0 = dicht nebeneinander)
BAR_SPACING = 1.4

COMPONENT_COLORS = {
    # Hauptelemente mit Aufschlüsselung
    "Semesterticket": "#f00c0c",  # rot
    "Studierendenwerksbeitrag": "#ff7f0e",  # orange
    "Studierendenschaftsbeitrag": "#2ca02c",  # grün
    "Verwaltungskostenbeitrag": "#1f77b4",  # blau
    "Leihfahrradsystem": "#9467bd",  # lila
    "Kulturticket": "#8c564b",  # braun

    # Sonstige / historische Posten
    "Studiengebühren": "#7f7f7f",  # grau
    "Keine Aufschlüsselung verfügbar": "#17becf",  # türkis
}


def get_color_for_component(name: str):
    try:
        return COMPONENT_COLORS[name]
    except KeyError:
        raise KeyError(f"Unbekannte Komponente ohne definierte Farbe: {name!r}. "
                       f"Bitte eine Farbe in COMPONENT_COLORS hinterlegen.")


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
    # Studierendenwerksbeitrag / Studentenwerk vereinheitlichen
    if "studierendenwerk" in n or "studentenwerk" in n:
        return "Studierendenwerksbeitrag"
    # Studierendenschaft / AStA / Theaterticket -> einheitlich als Studierendenschaftsbeitrag
    if "studierendenschaft" in n or "asta" in n or "theaterticket" in n:
        return "Studierendenschaftsbeitrag"
    if "kulturticket" in n:
        return "Kulturticket"
    if "studiengebühren" in n or "studiengebuehren" in n:
        return "Studiengebühren"
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
    all_names = set()
    values_map = {}

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
                # für Statistik speichern (nur echte numerische Beiträge)
                values_map.setdefault(canonical, []).append(v)
            all_names.add(canonical)
        rows.append({"label": name, "comps": comp_map, "raw": e})

    # Bestimme Komponentenreihenfolge anhand von Stabilität (Varianz) und Häufigkeit
    if all_names:
        total_rows = max(1, len(rows))
        stats = []
        for nm in all_names:
            vals = values_map.get(nm, [])
            n = len(vals)
            if n > 0:
                mean = sum(vals) / n
                var = sum((x - mean) ** 2 for x in vals) / n  # Populationsvarianz
                freq = n / total_rows
            else:
                var = float("inf")  # selten/nie numerisch angegeben -> ans Ende
                freq = 0.0
            stats.append((nm, var, freq))
        # Sortierung: niedrige Varianz zuerst (stabil), dann höhere Häufigkeit, dann Name
        components_order = [t[0] for t in sorted(stats, key=lambda t: (t[1], -t[2], t[0].lower()))]
    else:
        components_order = []

    # Sicherstellen, dass "Studiengebühren" (falls vorhanden) zuletzt steht,
    # damit diese Komponente im gestapelten Plot oben sichtbar ist.
    if "Studiengebühren" in components_order:
        components_order = [c for c in components_order if c != "Studiengebühren"] + ["Studiengebühren"]

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
            return f"{int(round(v))}€"
        # Sonst mit zwei Nachkommastellen
        return f"{v:.2f}€"
    except Exception:
        return f"{v}€"


def plot_and_save(labels, totals, stack_values, components_order):
    if not labels:
        print("Keine Daten zum Plotten gefunden.")
        return
    # x-Positionen mit Abstandsfaktor skalieren, damit Labels nicht ineinander buggen
    x = [i * BAR_SPACING for i in range(len(labels))]
    known_totals = [t for t in totals if t is not None and t > 0]
    max_known = max(known_totals) if known_totals else 1.0

    # Figurbreite proportional zur Anzahl der Labels und zum Abstandsfaktor
    fig_width = max(10, len(labels) * 0.45 * BAR_SPACING)
    plt.figure(figsize=(fig_width, 7.0))
    ax = plt.gca()

    bottom = [0] * len(labels)
    bar_width = 0.65 * BAR_SPACING
    for comp in components_order:
        vals = stack_values[comp]
        color = get_color_for_component(comp)
        ax.bar(x, vals, bottom=bottom, color=color, label=comp, edgecolor='white', width=bar_width)
        bottom = [bottom[i] + vals[i] for i in range(len(bottom))]

    # ensure y-limits leave space for annotations
    top_value = max(max(bottom) if bottom else 0.0, max_known)
    ax.set_ylim(0, top_value * 1.12)

    # annotate totals or placeholder (mit lesbarem Hintergrund)
    for i, lbl in enumerate(labels):
        if totals[i] is not None:
            ax.text(
                x[i],
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
            ax.bar(x[i], placeholder_height, color="#eeeeee", edgecolor="#999999", hatch='//', width=bar_width,
                   zorder=5)
            ax.text(
                x[i],
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
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("Euro")
    ax.set_title("Zusammensetzung Semesterbeitrag (gestapelt)")

    fig = plt.gcf()
    has_ss24 = any("Sommersemester 2024" in str(lbl) for lbl in labels)

    # Legendenlabels ggf. mit Sternchen versehen (nur Legende, nicht Daten/Stack)
    handles, leg_labels = ax.get_legend_handles_labels()
    if has_ss24:
        leg_labels = [("Semesterticket*" if l == "Semesterticket" else l) for l in leg_labels]

    # etwas mehr Platz rechts für Legende + Hinweis
    fig.subplots_adjust(right=0.78, bottom=0.16)  # <- bottom erhöht (war 0.10)

    # Haupt-Legende (Komponenten) rechts oben
    legend_main = ax.legend(
        handles,
        leg_labels,
        title="Komponenten",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        fontsize=8,
        borderaxespad=0.0,
    )
    ax.add_artist(legend_main)

    # Hinweis als Textbox direkt unterhalb der Komponenten-Legende (an Legenden-Box gekoppelt)
    if has_ss24:
        fig.canvas.draw()  # benötigt, damit legend_main eine korrekte bbox hat
        bbox_fig = legend_main.get_window_extent(fig.canvas.get_renderer()).transformed(fig.transFigure.inverted())

        fig.text(
            bbox_fig.x0,  # links bündig zur Legende
            max(0.01, bbox_fig.y0 - 0.02),  # knapp darunter; clamp gegen negativ
            "* Ab SoSe 2024: RMV-Semesterticket → Deutschlandticket",
            ha="left",
            va="top",
            fontsize=7,
            bbox={"facecolor": "white", "alpha": 0.9, "pad": 2, "edgecolor": "#dddddd"},
        )

    # kein tight_layout, damit die manuelle Platzierung nicht verschoben wird

    os.makedirs(OUT_DIR, exist_ok=True)
    plt.savefig(
        PNG_PATH,
        dpi=150,
        bbox_inches="tight",  # <- verhindert Abschneiden (unten/rechts)
        pad_inches=0.15,  # <- kleiner Sicherheitsrand
    )
    plt.close()
    print("Plot gespeichert:", PNG_PATH)


def main():
    entries = load_entries()
    labels, rows, components_order = build_table(entries)
    totals, stack_values, missing_flags = totals_and_stacks(labels, rows, components_order)
    plot_and_save(labels, totals, stack_values, components_order)


if __name__ == "__main__":
    main()
