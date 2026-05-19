import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001")
SRC = BASE / "measured" / "traversal_windows_v0.csv"
OUT = BASE / "measured" / "boundary_deformation_surface_v1.csv"

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

for r in rows:
    r["window_size"] = int(float(r["window_size"]))
    r["line_start"] = int(float(r["line_start"]))
    r["line_end"] = int(float(r["line_end"]))
    r["stable_share"] = float(r["stable_share"])
    r["middle_share"] = float(r["middle_share"])
    r["residual_share"] = float(r["residual_share"])

sizes = sorted(set(r["window_size"] for r in rows))

def dominant(r):
    vals = {
        "stable": r["stable_share"],
        "middle": r["middle_share"],
        "residual": r["residual_share"],
    }
    return max(vals, key=vals.get)

def segments_for(size):
    rs = [r for r in rows if r["window_size"] == size]
    rs = sorted(rs, key=lambda x: x["line_start"])

    segs = []
    current = None

    for r in rs:
        d = dominant(r)

        if current is None:
            current = {
                "window_size": size,
                "dominant": d,
                "start": r["line_start"],
                "end": r["line_end"],
                "stable_mass": r["stable_share"],
                "middle_mass": r["middle_share"],
                "residual_mass": r["residual_share"],
                "count": 1,
            }
            continue

        if d == current["dominant"] and r["line_start"] <= current["end"] + 1:
            current["end"] = r["line_end"]
            current["stable_mass"] += r["stable_share"]
            current["middle_mass"] += r["middle_share"]
            current["residual_mass"] += r["residual_share"]
            current["count"] += 1
        else:
            segs.append(current)
            current = {
                "window_size": size,
                "dominant": d,
                "start": r["line_start"],
                "end": r["line_end"],
                "stable_mass": r["stable_share"],
                "middle_mass": r["middle_share"],
                "residual_mass": r["residual_share"],
                "count": 1,
            }

    if current is not None:
        segs.append(current)

    for s in segs:
        s["width"] = s["end"] - s["start"] + 1
        s["center"] = (s["start"] + s["end"]) / 2
        s["avg_stable"] = s["stable_mass"] / s["count"]
        s["avg_middle"] = s["middle_mass"] / s["count"]
        s["avg_residual"] = s["residual_mass"] / s["count"]

    return segs

def overlap(a, b):
    s = max(a["start"], b["start"])
    e = min(a["end"], b["end"])
    if e < s:
        return 0
    return e - s + 1

def classify(prev, cur, ov):
    if ov == 0:
        return "appears"

    from_ratio = ov / prev["width"]
    to_ratio = ov / cur["width"]
    center_shift = cur["center"] - prev["center"]
    width_ratio = cur["width"] / prev["width"] if prev["width"] else 0

    if prev["dominant"] != cur["dominant"]:
        if cur["dominant"] == "middle":
            return "embedded_seam"
        return "boundary_recolored"

    if abs(center_shift) <= max(25, 0.05 * prev["width"]) and 0.8 <= width_ratio <= 1.25:
        return "stable_boundary"

    if width_ratio >= 1.5:
        return "widening_boundary"

    if width_ratio <= 0.67:
        return "thinning_boundary"

    if abs(center_shift) > max(25, 0.2 * prev["width"]):
        return "slow_drift"

    if cur["avg_middle"] > prev["avg_middle"] + 0.05:
        return "reintegration_pocket"

    return "minor_deformation"

out = []

for i in range(len(sizes) - 1):
    from_size = sizes[i]
    to_size = sizes[i + 1]

    prevs = segments_for(from_size)
    curs = segments_for(to_size)

    matched_prev = set()
    matched_cur = set()

    for ci, cur in enumerate(curs):
        candidates = []
        for pi, prev in enumerate(prevs):
            ov = overlap(prev, cur)
            if ov > 0:
                candidates.append((ov, pi, prev))

        if not candidates:
            out.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_segment": "",
                "to_segment": ci + 1,
                "from_dominant": "",
                "to_dominant": cur["dominant"],
                "from_interval": "",
                "to_interval": f'{cur["start"]}-{cur["end"]}',
                "overlap_lines": 0,
                "center_shift": "",
                "width_change": "",
                "relation_type": "appears",
                "boundary_note": "new dominant segment appears at wider constitution",
            })
            matched_cur.add(ci)
            continue

        candidates.sort(reverse=True, key=lambda x: x[0])
        ov, pi, prev = candidates[0]
        matched_prev.add(pi)
        matched_cur.add(ci)

        center_shift = cur["center"] - prev["center"]
        width_change = cur["width"] - prev["width"]
        rel = classify(prev, cur, ov)

        out.append({
            "from_window_size": from_size,
            "to_window_size": to_size,
            "from_segment": pi + 1,
            "to_segment": ci + 1,
            "from_dominant": prev["dominant"],
            "to_dominant": cur["dominant"],
            "from_interval": f'{prev["start"]}-{prev["end"]}',
            "to_interval": f'{cur["start"]}-{cur["end"]}',
            "overlap_lines": ov,
            "center_shift": round(center_shift, 2),
            "width_change": width_change,
            "relation_type": rel,
            "boundary_note": "observer-side boundary deformation under adjacent constitution transition",
        })

    for pi, prev in enumerate(prevs):
        if pi not in matched_prev:
            out.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_segment": pi + 1,
                "to_segment": "",
                "from_dominant": prev["dominant"],
                "to_dominant": "",
                "from_interval": f'{prev["start"]}-{prev["end"]}',
                "to_interval": "",
                "overlap_lines": 0,
                "center_shift": "",
                "width_change": "",
                "relation_type": "boundary_disappearance",
                "boundary_note": "prior dominant segment not preserved at wider constitution",
            })

fields = [
    "from_window_size",
    "to_window_size",
    "from_segment",
    "to_segment",
    "from_dominant",
    "to_dominant",
    "from_interval",
    "to_interval",
    "overlap_lines",
    "center_shift",
    "width_change",
    "relation_type",
    "boundary_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

print("WROTE", OUT.resolve())
print("ROWS", len(out))
