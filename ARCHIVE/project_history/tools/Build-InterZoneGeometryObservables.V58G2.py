#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


OUT_FIELDS = [
    "terrain_id",
    "territory_start",
    "territory_end",
    "territory_width",
    "candidate_count",
    "candidate_span_total",
    "candidate_span_ratio",
    "quiet_span_total",
    "quiet_span_ratio",
    "quiet_gap_count",
    "largest_quiet_gap",
    "mean_quiet_gap",
    "candidate_width_min",
    "candidate_width_mean",
    "candidate_width_max",
    "candidate_spacing_min",
    "candidate_spacing_mean",
    "candidate_spacing_max",
    "first_candidate_start",
    "last_candidate_end",
    "occupied_extent",
    "occupied_extent_ratio",
    "edge_left_quiet",
    "edge_right_quiet",
]


def read_csv(path):
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8-sig", newline="") as f:
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


def to_int(v, default=0):
    try:
        return int(float(v))
    except Exception:
        return default


def mean(values):
    if not values:
        return 0.0
    return sum(values) / len(values)


def fmt_ratio(v):
    return f"{v:.6f}"


def build_row(terrain_id, zones, territory_start, territory_end):
    territory_width = max(0, territory_end - territory_start + 1)

    clean = []
    for z in zones:
        start = to_int(z.get("span_start"))
        end = to_int(z.get("span_end"))

        if end < territory_start:
            continue
        if start > territory_end:
            continue

        start = max(start, territory_start)
        end = min(end, territory_end)

        if end >= start:
            clean.append({
                "start": start,
                "end": end,
                "width": end - start + 1,
            })

    clean.sort(key=lambda x: (x["start"], x["end"]))

    candidate_count = len(clean)

    if candidate_count == 0:
        return {
            "terrain_id": terrain_id,
            "territory_start": territory_start,
            "territory_end": territory_end,
            "territory_width": territory_width,
            "candidate_count": 0,
            "candidate_span_total": 0,
            "candidate_span_ratio": fmt_ratio(0.0),
            "quiet_span_total": territory_width,
            "quiet_span_ratio": fmt_ratio(1.0 if territory_width else 0.0),
            "quiet_gap_count": 0,
            "largest_quiet_gap": 0,
            "mean_quiet_gap": fmt_ratio(0.0),
            "candidate_width_min": 0,
            "candidate_width_mean": fmt_ratio(0.0),
            "candidate_width_max": 0,
            "candidate_spacing_min": 0,
            "candidate_spacing_mean": fmt_ratio(0.0),
            "candidate_spacing_max": 0,
            "first_candidate_start": 0,
            "last_candidate_end": 0,
            "occupied_extent": 0,
            "occupied_extent_ratio": fmt_ratio(0.0),
            "edge_left_quiet": territory_width,
            "edge_right_quiet": 0,
        }

    widths = [z["width"] for z in clean]
    candidate_span_total = sum(widths)
    candidate_span_ratio = candidate_span_total / territory_width if territory_width else 0.0

    quiet_span_total = max(0, territory_width - candidate_span_total)
    quiet_span_ratio = quiet_span_total / territory_width if territory_width else 0.0

    spacings = []
    for i in range(1, candidate_count):
        gap = clean[i]["start"] - clean[i - 1]["end"] - 1
        if gap > 0:
            spacings.append(gap)

    quiet_gap_count = len(spacings)
    largest_quiet_gap = max(spacings) if spacings else 0
    mean_quiet_gap = mean(spacings)

    first_candidate_start = clean[0]["start"]
    last_candidate_end = clean[-1]["end"]
    occupied_extent = max(0, last_candidate_end - first_candidate_start + 1)
    occupied_extent_ratio = occupied_extent / territory_width if territory_width else 0.0

    edge_left_quiet = max(0, first_candidate_start - territory_start)
    edge_right_quiet = max(0, territory_end - last_candidate_end)

    all_spacing = []
    for i in range(1, candidate_count):
        all_spacing.append(max(0, clean[i]["start"] - clean[i - 1]["end"] - 1))

    return {
        "terrain_id": terrain_id,
        "territory_start": territory_start,
        "territory_end": territory_end,
        "territory_width": territory_width,
        "candidate_count": candidate_count,
        "candidate_span_total": candidate_span_total,
        "candidate_span_ratio": fmt_ratio(candidate_span_ratio),
        "quiet_span_total": quiet_span_total,
        "quiet_span_ratio": fmt_ratio(quiet_span_ratio),
        "quiet_gap_count": quiet_gap_count,
        "largest_quiet_gap": largest_quiet_gap,
        "mean_quiet_gap": fmt_ratio(mean_quiet_gap),
        "candidate_width_min": min(widths),
        "candidate_width_mean": fmt_ratio(mean(widths)),
        "candidate_width_max": max(widths),
        "candidate_spacing_min": min(all_spacing) if all_spacing else 0,
        "candidate_spacing_mean": fmt_ratio(mean(all_spacing)),
        "candidate_spacing_max": max(all_spacing) if all_spacing else 0,
        "first_candidate_start": first_candidate_start,
        "last_candidate_end": last_candidate_end,
        "occupied_extent": occupied_extent,
        "occupied_extent_ratio": fmt_ratio(occupied_extent_ratio),
        "edge_left_quiet": edge_left_quiet,
        "edge_right_quiet": edge_right_quiet,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--terrain-id", required=True)
    ap.add_argument("--candidate-zones-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--territory-start", required=True, type=int)
    ap.add_argument("--territory-end", required=True, type=int)
    args = ap.parse_args()

    zones = read_csv(args.candidate_zones_csv)

    row = build_row(
        args.terrain_id,
        zones,
        args.territory_start,
        args.territory_end,
    )

    write_csv(args.out_csv, [row])
    print(f"WROTE {args.out_csv}")
    print("ROWS 1")


if __name__ == "__main__":
    main()
