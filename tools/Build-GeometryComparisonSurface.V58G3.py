#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from html import escape


FIELDS = [
    "terrain_id",
    "candidate_count",
    "candidate_span_ratio",
    "quiet_gap_count",
    "largest_quiet_gap",
    "candidate_width_mean",
    "candidate_spacing_mean",
    "occupied_extent_ratio",
]


def read_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDS})
    tmp.replace(out)


def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def to_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def compact_name(name):
    return (
        name.replace("openstack_long_horizon_001_slice_", "OpenStack ")
            .replace("linux_long_horizon_001_slice_", "Linux ")
            .replace("apache_baseline_slice_", "Apache ")
            .replace("_", " ")
    )


def strip_bar(span_ratio, gap_count, width=50):
    occupied = max(0, min(width, round(to_float(span_ratio) * width)))
    if occupied == 0:
        return "." * width
    if gap_count <= 0:
        return "#" * occupied + "." * (width - occupied)

    parts = gap_count + 1
    occ_each = max(1, occupied // parts)
    quiet_total = max(0, width - occupied)
    gap_each = max(1, quiet_total // gap_count) if gap_count else 0

    out = []
    for i in range(parts):
        out.append("#" * occ_each)
        if i < gap_count:
            out.append("." * gap_each)

    s = "".join(out)
    if len(s) < width:
        s += "." * (width - len(s))
    return s[:width]


def html_page(rows):
    html = []
    html.append("<!doctype html><html><head><meta charset='utf-8'>")
    html.append("<title>Geometry Comparison Surface V0</title>")
    html.append("""
<style>
body { font-family: system-ui, sans-serif; margin: 24px; background: #fbfbfb; color: #222; }
h1 { font-size: 22px; margin-bottom: 4px; }
.note { max-width: 1100px; color: #555; line-height: 1.4; margin-bottom: 18px; }
table { border-collapse: collapse; font-size: 13px; width: 100%; }
th, td { border-bottom: 1px solid #ddd; padding: 6px 8px; text-align: right; }
th:first-child, td:first-child { text-align: left; }
th:nth-child(2), td:nth-child(2) { text-align: left; }
.bar { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; letter-spacing: 1px; color: #222; white-space: pre; }
.small { color: #666; font-size: 12px; margin-top: 14px; }
</style>
""")
    html.append("</head><body>")
    html.append("<h1>Geometry Comparison Surface V0</h1>")
    html.append("<div class='note'>Inter-zone geometry comparison. This exposes already-earned observables: occupied candidate span, quiet gaps, spacing, and occupied extent. It does not create geometry labels, classifications, rankings, anomaly claims, basin claims, movement claims, or explanations.</div>")
    html.append("<table>")
    html.append("<tr><th>Terrain</th><th>Strip</th><th>Candidates</th><th>Span%</th><th>Gaps</th><th>Largest gap</th><th>Width mean</th><th>Spacing mean</th><th>Occupied extent%</th></tr>")

    for r in rows:
        terrain = r.get("terrain_id", "")
        bar = strip_bar(r.get("candidate_span_ratio", "0"), to_int(r.get("quiet_gap_count", 0)))
        html.append(
            "<tr>"
            f"<td>{escape(compact_name(terrain))}</td>"
            f"<td class='bar'>{escape(bar)}</td>"
            f"<td>{escape(r.get('candidate_count',''))}</td>"
            f"<td>{to_float(r.get('candidate_span_ratio')):.3f}</td>"
            f"<td>{escape(r.get('quiet_gap_count',''))}</td>"
            f"<td>{escape(r.get('largest_quiet_gap',''))}</td>"
            f"<td>{to_float(r.get('candidate_width_mean')):.1f}</td>"
            f"<td>{to_float(r.get('candidate_spacing_mean')):.1f}</td>"
            f"<td>{to_float(r.get('occupied_extent_ratio')):.3f}</td>"
            "</tr>"
        )

    html.append("</table>")
    html.append("<div class='small'># = occupied candidate span proxy. . = quiet territory proxy. Strip is schematic, not a measured pixel map.</div>")
    html.append("</body></html>")
    return "\n".join(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-html", required=True)
    args = ap.parse_args()

    rows = read_csv(args.input_csv)
    rows.sort(key=lambda r: r.get("terrain_id", ""))

    write_csv(args.out_csv, rows)

    out_html = Path(args.out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_page(rows), encoding="utf-8")

    print(f"WROTE {args.out_csv}")
    print(f"WROTE {args.out_html}")
    print(f"ROWS {len(rows)}")


if __name__ == "__main__":
    main()
