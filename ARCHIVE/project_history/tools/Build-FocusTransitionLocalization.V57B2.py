#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from collections import Counter


OUT_FIELDS = [
    "terrain_id",
    "bin_id",
    "bin_start",
    "bin_end",
    "total_transitions",
    "persisted_count",
    "smoothed_count",
    "fragmented_count",
    "posture_changed_count",
    "recomposed_count",
    "non_persisted_count",
    "non_persisted_share",
    "dominant_transition_marker",
    "localization_class",
]


def parse_int(row, name):
    try:
        return int(row[name])
    except KeyError:
        raise SystemExit(f"MISSING_REQUIRED_COLUMN {name}")
    except ValueError:
        raise SystemExit(f"BAD_INT {name}={row.get(name)}")


def get_text(row, name):
    if name not in row:
        raise SystemExit(f"MISSING_REQUIRED_COLUMN {name}")
    return row[name]


def localization_class(non_persisted_count, non_persisted_share):
    if non_persisted_count == 0:
        return "quiet"
    if non_persisted_share < 0.05:
        return "distributed_low"
    if non_persisted_count < 10:
        return "localized_deformation"
    return "dense_deformation"


def main():
    ap = argparse.ArgumentParser(
        description="Build observer-only focus transition localization surface."
    )
    ap.add_argument("--terrain-id", required=True)
    ap.add_argument("--transition-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--bin-size", required=True, type=int)
    args = ap.parse_args()

    if args.bin_size <= 0:
        raise SystemExit("BAD_BIN_SIZE")

    in_path = Path(args.transition_csv)
    out_path = Path(args.out_csv)

    rows = []
    max_end = 0

    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = ["from_line_start", "from_line_end", "transition_marker"]
        for col in required:
            if col not in reader.fieldnames:
                raise SystemExit(f"MISSING_REQUIRED_COLUMN {col}")

        for row in reader:
            start = parse_int(row, "from_line_start")
            end = parse_int(row, "from_line_end")
            marker = get_text(row, "transition_marker")

            if end < start:
                raise SystemExit(f"BAD_SPAN {start}-{end}")

            rows.append((start, end, marker))
            if end > max_end:
                max_end = end

    bins = []
    pos = 1
    bin_index = 1
    while pos <= max_end:
        end = min(pos + args.bin_size - 1, max_end)
        bins.append({
            "bin_id": f"bin_{bin_index:04d}",
            "bin_start": pos,
            "bin_end": end,
            "markers": Counter(),
        })
        pos = end + 1
        bin_index += 1

    for start, end, marker in rows:
        first_bin = (start - 1) // args.bin_size
        last_bin = (end - 1) // args.bin_size

        for idx in range(first_bin, last_bin + 1):
            if idx < 0 or idx >= len(bins):
                continue
            bins[idx]["markers"][marker] += 1

    out_rows = []
    for b in bins:
        markers = b["markers"]
        total = sum(markers.values())

        persisted = markers.get("persisted", 0)
        smoothed = markers.get("smoothed", 0)
        fragmented = markers.get("fragmented", 0)
        posture_changed = markers.get("posture_changed", 0)
        recomposed = markers.get("recomposed", 0)

        non_persisted = total - persisted
        non_persisted_share = 0.0
        if total > 0:
            non_persisted_share = non_persisted / total

        dominant = ""
        if total > 0:
            dominant = markers.most_common(1)[0][0]

        out_rows.append({
            "terrain_id": args.terrain_id,
            "bin_id": b["bin_id"],
            "bin_start": b["bin_start"],
            "bin_end": b["bin_end"],
            "total_transitions": total,
            "persisted_count": persisted,
            "smoothed_count": smoothed,
            "fragmented_count": fragmented,
            "posture_changed_count": posture_changed,
            "recomposed_count": recomposed,
            "non_persisted_count": non_persisted,
            "non_persisted_share": f"{non_persisted_share:.4f}",
            "dominant_transition_marker": dominant,
            "localization_class": localization_class(non_persisted, non_persisted_share),
        })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)

    tmp_path.replace(out_path)
    print(f"WROTE {out_path}")
    print(f"ROWS {len(out_rows)}")


if __name__ == "__main__":
    main()
