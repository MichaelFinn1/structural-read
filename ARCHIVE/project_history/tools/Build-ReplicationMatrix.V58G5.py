#!/usr/bin/env python3
import argparse
import csv
import math
from pathlib import Path
from html import escape


METRICS = [
    "candidate_count",
    "candidate_span_ratio",
    "quiet_gap_count",
    "largest_quiet_gap",
    "occupied_extent_ratio",
]

OUT_FIELDS = [
    "family_name",
    "terrain_member",
    "slice_count",
    "candidate_count_mean",
    "candidate_span_ratio_mean",
    "quiet_gap_count_mean",
    "largest_quiet_gap_mean",
    "occupied_extent_ratio_mean",
    "within_member_persistence_score",
]


def read_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    tmp.replace(out)


def to_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def sd(xs):
    if len(xs) <= 1:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def cv_stability(xs):
    m = mean(xs)
    s = sd(xs)
    if m == 0:
        return 1.0 if s == 0 else 0.0
    return 1.0 / (1.0 + (s / abs(m)))


def strip_slice_suffix(name):
    for suffix in ["_slice_A", "_slice_B", "_slice_C"]:
        if name.endswith(suffix):
            return name[:-len(suffix)]
    return name


def default_family(member):
    if member.startswith("openstack"):
        return "openstack"
    if member.startswith("linux"):
        return "linux"
    if member.startswith("apache"):
        return "apache"
    return "unassigned"


def load_registry(path):
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    rows = read_csv(p)
    out = {}
    for r in rows:
        member = r.get("terrain_member", "").strip()
        family = r.get("family_name", "").strip()
        if member and family:
            out[member] = family
    return out


def summarize_member(family, member, rows):
    result = {
        "family_name": family,
        "terrain_member": member,
        "slice_count": str(len(rows)),
    }

    stability = []

    for metric in METRICS:
        vals = [to_float(r.get(metric, 0)) for r in rows]
        result[f"{metric}_mean"] = f"{mean(vals):.6f}"
        stability.append(cv_stability(vals))

    result["within_member_persistence_score"] = f"{mean(stability):.6f}"
    return result


def html_page(rows):
    html = []
    html.append("<!doctype html><html><head><meta charset='utf-8'>")
    html.append("<title>Replication Matrix V0</title>")
    html.append("""
<style>
body { font-family: system-ui, sans-serif; margin: 24px; background: #fbfbfb; color: #222; }
h1 { font-size: 22px; margin-bottom: 4px; }
.note { max-width: 1100px; color: #555; line-height: 1.4; margin-bottom: 18px; }
table { border-collapse: collapse; font-size: 13px; width: 100%; margin-bottom: 28px; }
th, td { border-bottom: 1px solid #ddd; padding: 6px 8px; text-align: right; }
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align: left; }
.family { margin-top: 24px; font-size: 17px; font-weight: 700; }
.small { color: #666; font-size: 12px; margin-top: 12px; }
</style>
""")
    html.append("</head><body>")
    html.append("<h1>Replication Matrix V0</h1>")
    html.append("<div class='note'>Replication surface for already-earned inter-zone geometry observables. This asks whether geometry-like distinctions remain available across repeated contact. It does not create geometry labels, classifications, rankings, anomaly claims, basin claims, movement claims, or interpretations.</div>")

    current = None
    for r in rows:
        family = r.get("family_name", "")
        if family != current:
            if current is not None:
                html.append("</table>")
            current = family
            html.append(f"<div class='family'>{escape(family)}</div>")
            html.append("<table>")
            html.append("<tr><th>Terrain member</th><th>Slices</th><th>Persistence</th><th>Candidate mean</th><th>Span mean</th><th>Gap mean</th><th>Largest gap mean</th><th>Occupied extent mean</th></tr>")

        html.append(
            "<tr>"
            f"<td>{escape(r.get('terrain_member',''))}</td>"
            f"<td>{escape(r.get('slice_count',''))}</td>"
            f"<td>{float(r.get('within_member_persistence_score',0)):.3f}</td>"
            f"<td>{float(r.get('candidate_count_mean',0)):.3f}</td>"
            f"<td>{float(r.get('candidate_span_ratio_mean',0)):.3f}</td>"
            f"<td>{float(r.get('quiet_gap_count_mean',0)):.3f}</td>"
            f"<td>{float(r.get('largest_quiet_gap_mean',0)):.3f}</td>"
            f"<td>{float(r.get('occupied_extent_ratio_mean',0)):.3f}</td>"
            "</tr>"
        )

    if rows:
        html.append("</table>")

    html.append("<div class='small'>Persistence is a check surface only. Geometry comparison remains the observer surface. No new vocabulary is created here.</div>")
    html.append("</body></html>")
    return "\\n".join(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geometry-csv", required=True)
    ap.add_argument("--registry-csv", required=False)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-html", required=True)
    args = ap.parse_args()

    rows = read_csv(args.geometry_csv)
    registry = load_registry(args.registry_csv)

    grouped = {}
    for row in rows:
        terrain_id = row.get("terrain_id", "")
        member = strip_slice_suffix(terrain_id)
        family = registry.get(member, default_family(member))
        key = (family, member)
        grouped.setdefault(key, []).append(row)

    out_rows = []
    for family, member in sorted(grouped.keys()):
        out_rows.append(summarize_member(family, member, grouped[(family, member)]))

    write_csv(args.out_csv, out_rows, OUT_FIELDS)

    out_html = Path(args.out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_page(out_rows), encoding="utf-8")

    print(f"WROTE {args.out_csv}")
    print(f"WROTE {args.out_html}")
    print(f"ROWS {len(out_rows)}")


if __name__ == "__main__":
    main()
