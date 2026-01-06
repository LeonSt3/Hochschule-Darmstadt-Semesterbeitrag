import os
import json
import re
import matplotlib.pyplot as plt
import itertools
from datetime import datetime

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_PATH = os.path.join(OUT_DIR, "history.json")
LATEST_PATH = os.path.join(OUT_DIR, "latest.json")
PNG_PATH = os.path.join(OUT_DIR, "semester_plot.png")

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

def load_entries():
    entries = []
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except:
            entries = []
    if not entries and os.path.exists(LATEST_PATH):
        try:
            with open(LATEST_PATH, "r", encoding="utf-8") as f:
                latest = json.load(f)
                entries = [latest]
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
            components_order = [it.get("name") for it in latest["items"] if it.get("name")]
    # fallback: build union of components
    all_names = set()
    for e in entries:
        name = e.get("semester") or e.get("total") or e.get("fetched_at") or datetime.utcnow().isoformat()
        labels.append(name)
        comp_map = {}
        for it in e.get("items", []):
            n = it.get("name")
            v = it.get("value") if "value" in it else it.get("amount")
            comp_map[n] = safe_num(v)
            all_names.add(n)
        rows.append({"label": name, "comps": comp_map, "raw": e})
    if not components_order:
        components_order = sorted([n for n in all_names if n], key=lambda x: x.lower())
    return labels, rows, components_order

def totals_and_stacks(labels, rows, components_order):
    stack_values = {c: [] for c in components_order}
    totals = []
    missing_flags = []
    for r in rows:
        comps = r["comps"]
        vals = []
        missing = False
        total = 0.0
        # compute total: if any component missing -> mark missing
        for c in components_order:
            v = comps.get(c)
            if v is None:
                missing = True
            else:
                total += v
            stack_values[c].append(v if v is not None else 0.0)
        totals.append(total if not missing else None)
        missing_flags.append(missing)
    return totals, stack_values, missing_flags

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

    # annotate totals or placeholder
    for i, lbl in enumerate(labels):
        if totals[i] is not None:
            ax.text(i, totals[i] + max_known * 0.02, f"{totals[i]:.2f} €", ha="center", va="bottom", fontsize=8)
        else:
            placeholder_height = max_known * 0.03
            ax.bar(i, placeholder_height, color="#eeeeee", edgecolor="#999999", hatch='//', width=0.7)
            ax.text(i, placeholder_height + max_known * 0.02, "n.a.", ha="center", va="bottom", fontsize=8, color="#555555")

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
