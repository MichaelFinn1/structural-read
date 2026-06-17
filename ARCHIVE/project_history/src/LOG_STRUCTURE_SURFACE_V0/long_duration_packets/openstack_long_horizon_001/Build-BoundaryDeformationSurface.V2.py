import csv
from pathlib import Path

BASE = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001")
SRC = BASE / "measured" / "traversal_windows_v0.csv"
OUT = BASE / "measured" / "boundary_deformation_surface_v2.csv"

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
    rs = sorted(
        [r for r in rows if r["window_size"] == size],
        key=lambda x: x["line_start"]
    )

    segs = []
    cur = None

    for r in rs:
        d = dominant(r)

        if cur is None:
            cur = {
                "dominant": d,
                "start": r["line_start"],
                "end": r["line_end"],
                "stable_mass": r["stable_share"],
                "middle_mass": r["middle_share"],
                "residual_mass": r["residual_share"],
                "count": 1,
            }
            continue

        if d == cur["dominant"] and r["line_start"] <= cur["end"] + 1:
            cur["end"] = r["line_end"]
            cur["stable_mass"] += r["stable_share"]
            cur["middle_mass"] += r["middle_share"]
            cur["residual_mass"] += r["residual_share"]
            cur["count"] += 1
        else:
            segs.append(cur)
            cur = {
                "dominant": d,
                "start": r["line_start"],
                "end": r["line_end"],
                "stable_mass": r["stable_share"],
                "middle_mass": r["middle_share"],
                "residual_mass": r["residual_share"],
                "count": 1,
            }

    if cur is not None:
        segs.append(cur)

    for i, s in enumerate(segs, start=1):
        s["segment_id"] = i
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

def interval(s):
    return f'{s["start"]}-{s["end"]}'

def base_relation(prev, cur, ov):
    if ov <= 0:
        return "unmatched"

    from_ratio = ov / prev["width"]
    to_ratio = ov / cur["width"]

    if prev["dominant"] != cur["dominant"]:
        return "recolored_overlap"

    if from_ratio >= 0.67 and to_ratio >= 0.67:
        return "one_to_one_continuation"

    return "partial_continuation"

out = []

for i in range(len(sizes) - 1):
    from_size = sizes[i]
    to_size = sizes[i + 1]

    prevs = segments_for(from_size)
    curs = segments_for(to_size)

    prev_to_cur = {p["segment_id"]: [] for p in prevs}
    cur_to_prev = {c["segment_id"]: [] for c in curs}

    for p in prevs:
        for c in curs:
            ov = overlap(p, c)
            if ov > 0:
                item = {
                    "overlap": ov,
                    "from_ratio": ov / p["width"],
                    "to_ratio": ov / c["width"],
                    "prev": p,
                    "cur": c,
                }
                prev_to_cur[p["segment_id"]].append(item)
                cur_to_prev[c["segment_id"]].append(item)

    emitted_pairs = set()

    for p in prevs:
        links = prev_to_cur[p["segment_id"]]

        if not links:
            out.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_segment": p["segment_id"],
                "to_segment": "",
                "from_dominant": p["dominant"],
                "to_dominant": "",
                "from_interval": interval(p),
                "to_interval": "",
                "overlap_lines": 0,
                "from_overlap_count": 0,
                "to_overlap_count": "",
                "relation_type": "unmatched_disappearance",
                "relation_note": "prior segment has no overlap at wider constitution",
            })
            continue

        meaningful_links = [x for x in links if x["from_ratio"] >= 0.10 or x["to_ratio"] >= 0.10]

        if len(meaningful_links) > 1:
            for x in meaningful_links:
                c = x["cur"]
                key = (p["segment_id"], c["segment_id"])
                emitted_pairs.add(key)
                out.append({
                    "from_window_size": from_size,
                    "to_window_size": to_size,
                    "from_segment": p["segment_id"],
                    "to_segment": c["segment_id"],
                    "from_dominant": p["dominant"],
                    "to_dominant": c["dominant"],
                    "from_interval": interval(p),
                    "to_interval": interval(c),
                    "overlap_lines": x["overlap"],
                    "from_overlap_count": len(meaningful_links),
                    "to_overlap_count": len(cur_to_prev[c["segment_id"]]),
                    "relation_type": "one_to_many_split",
                    "relation_note": "one prior segment overlaps multiple wider-constitution segments",
                })

    for c in curs:
        links = cur_to_prev[c["segment_id"]]

        if not links:
            out.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_segment": "",
                "to_segment": c["segment_id"],
                "from_dominant": "",
                "to_dominant": c["dominant"],
                "from_interval": "",
                "to_interval": interval(c),
                "overlap_lines": 0,
                "from_overlap_count": "",
                "to_overlap_count": 0,
                "relation_type": "appears",
                "relation_note": "wider-constitution segment has no overlap from prior constitution",
            })
            continue

        meaningful_links = [x for x in links if x["from_ratio"] >= 0.10 or x["to_ratio"] >= 0.10]

        if len(meaningful_links) > 1:
            for x in meaningful_links:
                p = x["prev"]
                key = (p["segment_id"], c["segment_id"])
                emitted_pairs.add(key)
                out.append({
                    "from_window_size": from_size,
                    "to_window_size": to_size,
                    "from_segment": p["segment_id"],
                    "to_segment": c["segment_id"],
                    "from_dominant": p["dominant"],
                    "to_dominant": c["dominant"],
                    "from_interval": interval(p),
                    "to_interval": interval(c),
                    "overlap_lines": x["overlap"],
                    "from_overlap_count": len(prev_to_cur[p["segment_id"]]),
                    "to_overlap_count": len(meaningful_links),
                    "relation_type": "many_to_one_absorption",
                    "relation_note": "multiple prior segments overlap one wider-constitution segment",
                })

    for p in prevs:
        for x in prev_to_cur[p["segment_id"]]:
            c = x["cur"]
            key = (p["segment_id"], c["segment_id"])
            if key in emitted_pairs:
                continue

            from_count = len([z for z in prev_to_cur[p["segment_id"]] if z["from_ratio"] >= 0.10 or z["to_ratio"] >= 0.10])
            to_count = len([z for z in cur_to_prev[c["segment_id"]] if z["from_ratio"] >= 0.10 or z["to_ratio"] >= 0.10])

            if from_count > 1 or to_count > 1:
                continue

            rel = base_relation(p, c, x["overlap"])

            if rel == "partial_continuation" and x["from_ratio"] < 0.20 and x["to_ratio"] < 0.20:
                rel = "ambiguous_overlap"

            out.append({
                "from_window_size": from_size,
                "to_window_size": to_size,
                "from_segment": p["segment_id"],
                "to_segment": c["segment_id"],
                "from_dominant": p["dominant"],
                "to_dominant": c["dominant"],
                "from_interval": interval(p),
                "to_interval": interval(c),
                "overlap_lines": x["overlap"],
                "from_overlap_count": from_count,
                "to_overlap_count": to_count,
                "relation_type": rel,
                "relation_note": "observer-side overlap relation under adjacent constitution transition",
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
    "from_overlap_count",
    "to_overlap_count",
    "relation_type",
    "relation_note",
]

with OUT.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

print("WROTE", OUT.resolve())
print("ROWS", len(out))
