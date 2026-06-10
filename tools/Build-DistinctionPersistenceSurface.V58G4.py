#!/usr/bin/env python3
import argparse
import csv
import math
from pathlib import Path
from html import escape


OUT_FIELDS = [
    "terrain_family",
    "slice_count",

    "candidate_count_mean",
    "candidate_count_sd",

    "candidate_span_ratio_mean",
    "candidate_span_ratio_sd",

    "quiet_gap_count_mean",
    "quiet_gap_count_sd",

    "largest_quiet_gap_mean",
    "largest_quiet_gap_sd",

    "occupied_extent_ratio_mean",
    "occupied_extent_ratio_sd",

    "persistence_score",
]


METRICS = [
    "candidate_count",
    "candidate_span_ratio",
    "quiet_gap_count",
    "largest_quiet_gap",
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
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow(row)

    tmp.replace(out)


def to_float(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def sd(values):
    if len(values) <= 1:
        return 0.0
    m = mean(values)
    variance = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def cv_stability(values):
    m = mean(values)
    s = sd(values)

    if m == 0:
        if s == 0:
            return 1.0
        return 0.0

    cv = s / abs(m)
    return 1.0 / (1.0 + cv)


def terrain_family(terrain_id):
    name = terrain_id

    for suffix in ["_slice_A", "_slice_B", "_slice_C"]:
        if name.endswith(suffix):
            name = name[:-len(suffix)]

    return name


def fmt(v):
    return f"{v:.6f}"


def build_summary(rows):
    by_family = {}

    for row in rows:
        family = terrain_family(row.get("terrain_id", ""))
        by_family.setdefault(family, []).append(row)

    out = []

    for family in sorted(by_family.keys()):
        group = by_family[family]
        result = {
            "terrain_family": family,
            "slice_count": len(group),
        }

        stability_values = []

        for metric in METRICS:
            values = [to_float(r.get(metric, 0)) for r in group]
            metric_mean = mean(values)
            metric_sd = sd(values)

            result[f"{metric}_mean"] = fmt(metric_mean)
            result[f"{metric}_sd"] = fmt(metric_sd)

            stability_values.append(cv_stability(values))

        result["persistence_score"] = fmt(mean(stability_values))

        out.append(result)

    return out


def compact_family(name):
    return (
        name.replace("openstack_long_horizon_001", "OpenStack long horizon")
            .replace("linux_long_horizon_001", "Linux long horizon")
            .replace("apache_baseline", "Apache baseline")
            .replace("_", " ")
    )


def html_page(rows):
    html = []
    html.append("<!doctype html><html><head><meta charset='utf-8'>")
    html.append("<title>Distinction Persistence Surface V0</title>")
    html.append("""
<style>
body { font-family: system-ui, sans-serif; margin: 24px; background: #fbfbfb; color: #222; }
h1 { font-size: 22px; margin-bottom: 4px; }
.note { max-width: 1120px; color: #555; line-height: 1.4; margin-bottom: 18px; }
table { border-collapse: collapse; font-size: 13px; width: 100%; margin-bottom: 26px; }
th, td { border-bottom: 1px solid #ddd; padding: 6px 8px; text-align: right; }
th:first-child, td:first-child { text-align: left; }
.section { margin-top: 26px; font-size: 17px; font-weight: 700; }
.small { color: #666; font-size: 12px; margin-top: 12px; }
</style>
""")
    html.append("</head><body>")
    html.append("<h1>Distinction Persistence Surface V0</h1>")
    html.append("<div class='note'>Family-level stability summary from inter-zone geometry observables. Persistence score reflects lower variation across repeated slices. It is not importance, ranking, anomaly, basin, or interpretation.</div>")

    html.append("<table>")
    html.append("<tr><th>Family</th><th>Slices</th><th>Persistence</th><th>Candidate mean</th><th>Span mean</th><th>Gap mean</th><th>Largest gap mean</th><th>Occupied extent mean</th></tr>")

    for r in rows:
        html.append(
            "<tr>"
            f"<td>{escape(compact_family(r.get('terrain_family','')))}</td>"
            f"<td>{escape(str(r.get('slice_count','')))}</td>"
            f"<td>{float(r.get('persistence_score',0)):.3f}</td>"
            f"<td>{float(r.get('candidate_count_mean',0)):.3f}</td>"
            f"<td>{float(r.get('candidate_span_ratio_mean',0)):.3f}</td>"
            f"<td>{float(r.get('quiet_gap_count_mean',0)):.3f}</td>"
            f"<td>{float(r.get('largest_quiet_gap_mean',0)):.3f}</td>"
            f"<td>{float(r.get('occupied_extent_ratio_mean',0)):.3f}</td>"
            "</tr>"
        )

    html.append("</table>")

    html.append("<div class='section'>Metric means and variation</div>")
    html.append("<table>")
    html.append("<tr><th>Family</th><th>Metric</th><th>Mean</th><th>SD</th></tr>")

    for r in rows:
        family = compact_family(r.get("terrain_family", ""))
        for metric in METRICS:
            html.append(
                "<tr>"
                f"<td>{escape(family)}</td>"
                f"<td>{escape(metric)}</td>"
                f"<td>{float(r.get(metric + '_mean',0)):.6f}</td>"
                f"<td>{float(r.get(metric + '_sd',0)):.6f}</td>"
                "</tr>"
            )

    html.append("</table>")
    html.append("<div class='small'>Method: persistence score is the mean of coefficient-of-variation stability values across selected geometry observables. Higher means less variation across repeated slices. No geometry family labels are created.</div>")
    html.append("</body></html>")

    return "\n".join(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geometry-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--out-html", required=True)
    args = ap.parse_args()

    rows = read_csv(args.geometry_csv)
    summaries = build_summary(rows)

    write_csv(args.out_csv, summaries)

    out_html = Path(args.out_html)
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_page(summaries), encoding="utf-8")

    print(f"WROTE {args.out_csv}")
    print(f"WROTE {args.out_html}")
    print(f"ROWS {len(summaries)}")


if __name__ == "__main__":
    main()
