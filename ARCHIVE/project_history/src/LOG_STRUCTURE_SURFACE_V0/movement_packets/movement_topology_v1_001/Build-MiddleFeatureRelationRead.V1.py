import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_positions_v1.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_relation_read_v1.csv")

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(r["window_size"])
    r["middle_start"] = int(r["middle_start"])
    r["middle_end"] = int(r["middle_end"])
    r["middle_center"] = float(r["middle_center"])
    r["middle_width"] = int(r["middle_width"])

sizes = sorted(set(r["window_size"] for r in rows))

def overlap(a, b):
    start = max(a["middle_start"], b["middle_start"])
    end = min(a["middle_end"], b["middle_end"])
    if end < start:
        return 0
    return end - start + 1

def interval(r):
    return f"{r['middle_start']}-{r['middle_end']}"

out_rows = []

for i in range(len(sizes) - 1):
    from_size = sizes[i]
    to_size = sizes[i + 1]

    from_rows = [r for r in rows if r["window_size"] == from_size]
    to_rows = [r for r in rows if r["window_size"] == to_size]

    from_ids = {}
    to_ids = {}

    for ix, r in enumerate(from_rows, start=1):
        from_ids[id(r)] = f"{from_size}_feature_{ix:03d}"

    for ix, r in enumerate(to_rows, start=1):
        to_ids[id(r)] = f"{to_size}_feature_{ix:03d}"

    links = []

    for a in from_rows:
        for b in to_rows:
            ov = overlap(a, b)
            if ov <= 0:
                continue

            ratio_from = ov / max(1, a["middle_width"])
            ratio_to = ov / max(1, b["middle_width"])

            if ratio_from >= 0.2 or ratio_to >= 0.2:
                links.append({
                    "from": a,
                    "to": b,
                    "overlap": ov,
                    "ratio_from": ratio_from,
                    "ratio_to": ratio_to
                })

    from_link_counts = {}
    to_link_counts = {}

    for link in links:
        fkey = id(link["from"])
        tkey = id(link["to"])
        from_link_counts[fkey] = from_link_counts.get(fkey, 0) + 1
        to_link_counts[tkey] = to_link_counts.get(tkey, 0) + 1

    linked_from = set()
    linked_to = set()

    for link in links:
        a = link["from"]
        b = link["to"]
        fkey = id(a)
        tkey = id(b)

        linked_from.add(fkey)
        linked_to.add(tkey)

        if from_link_counts[fkey] > 1:
            relation = "splits"
        elif to_link_counts[tkey] > 1:
            relation = "merges"
        elif link["ratio_from"] >= 0.6 and link["ratio_to"] >= 0.6:
            if b["middle_width"] > a["middle_width"] + 10:
                relation = "widens"
            elif b["middle_width"] < a["middle_width"] - 10:
                relation = "thins"
            else:
                relation = "continues"
        elif link["ratio_from"] >= 0.25 or link["ratio_to"] >= 0.25:
            relation = "reconstitutes"
        else:
            relation = "ambiguous"

        out_rows.append({
            "from_window_size": from_size,
            "to_window_size": to_size,
            "from_feature_id": from_ids[fkey],
            "to_feature_id": to_ids[tkey],
            "from_interval": interval(a),
            "to_interval": interval(b),
            "from_center": a["middle_center"],
            "to_center": b["middle_center"],
            "center_delta": round(b["middle_center"] - a["middle_center"], 2),
            "overlap_lines": link["overlap"],
            "overlap_ratio_from": round(link["ratio_from"], 3),
            "overlap_ratio_to": round(link["ratio_to"], 3),
            "relation_type": relation,
            "boundary_note": "interval_overlap_relation_not_identity_proof"
        })

    for a in from_rows:
        if id(a) not in linked_from:
            out_rows.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_feature_id": from_ids[id(a)],
                "to_feature_id": "",
                "from_interval": interval(a),
                "to_interval": "",
                "from_center": a["middle_center"],
                "to_center": "",
                "center_delta": "",
                "overlap_lines": 0,
                "overlap_ratio_from": 0,
                "overlap_ratio_to": 0,
                "relation_type": "disappears",
                "boundary_note": "no_interval_overlap_at_next_constitution"
            })

    for b in to_rows:
        if id(b) not in linked_to:
            out_rows.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_feature_id": "",
                "to_feature_id": to_ids[id(b)],
                "from_interval": "",
                "to_interval": interval(b),
                "from_center": "",
                "to_center": b["middle_center"],
                "center_delta": "",
                "overlap_lines": 0,
                "overlap_ratio_from": 0,
                "overlap_ratio_to": 0,
                "relation_type": "appears",
                "boundary_note": "no_interval_overlap_from_prior_constitution"
            })

fields = [
    "from_window_size",
    "to_window_size",
    "from_feature_id",
    "to_feature_id",
    "from_interval",
    "to_interval",
    "from_center",
    "to_center",
    "center_delta",
    "overlap_lines",
    "overlap_ratio_from",
    "overlap_ratio_to",
    "relation_type",
    "boundary_note"
]

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(out_rows)

print("")
print("WROTE")
print(OUT.resolve())
print("")
