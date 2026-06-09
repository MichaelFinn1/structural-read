#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from collections import Counter


OUT_FIELDS = [
    "terrain_id",
    "candidate_id",
    "bin_size",
    "span_start",
    "span_end",
    "bin_count",
    "active_bin_count",
    "quiet_bin_count",
    "distributed_low_count",
    "localized_deformation_count",
    "dense_deformation_count",
    "dominant_localization_class",
    "candidate_type",
    "boundary_note",
]


ACTIVE_CLASSES = {
    "distributed_low",
    "localized_deformation",
    "dense_deformation",
}


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


def candidate_type(counts):
    distributed = counts.get("distributed_low", 0)
    localized = counts.get("localized_deformation", 0)
    dense = counts.get("dense_deformation", 0)

    active_classes = 0
    for value in (distributed, localized, dense):
        if value > 0:
            active_classes += 1

    if active_classes > 1:
        return "mixed_deformation_candidate"

    if dense > 0:
        return "dense_deformation_candidate"

    if localized > 0:
        return "localized_deformation_candidate"

    if distributed > 0:
        return "distributed_corridor_candidate"

    return "mixed_deformation_candidate"


def dominant_class(counts):
    if not counts:
        return ""
    return counts.most_common(1)[0][0]


def emit_candidate(args, idx, group):
    counts = Counter(row["localization_class"] for row in group)

    quiet = counts.get("quiet", 0)
    distributed = counts.get("distributed_low", 0)
    localized = counts.get("localized_deformation", 0)
    dense = counts.get("dense_deformation", 0)
    active = distributed + localized + dense

    return {
        "terrain_id": args.terrain_id,
        "candidate_id": f"candidate_{idx:04d}",
        "bin_size": args.bin_size,
        "span_start": group[0]["bin_start"],
        "span_end": group[-1]["bin_end"],
        "bin_count": len(group),
        "active_bin_count": active,
        "quiet_bin_count": quiet,
        "distributed_low_count": distributed,
        "localized_deformation_count": localized,
        "dense_deformation_count": dense,
        "dominant_localization_class": dominant_class(counts),
        "candidate_type": candidate_type(counts),
        "boundary_note": "quiet_bins_break_groups",
    }


def main():
    ap = argparse.ArgumentParser(
        description="Group adjacent active localization bins into observer-only candidate zones."
    )
    ap.add_argument("--terrain-id", required=True)
    ap.add_argument("--localization-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--bin-size", required=True, type=int)
    args = ap.parse_args()

    if args.bin_size <= 0:
        raise SystemExit("BAD_BIN_SIZE")

    in_path = Path(args.localization_csv)
    out_path = Path(args.out_csv)

    rows = []
    with in_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = ["bin_start", "bin_end", "localization_class"]
        for col in required:
            if col not in reader.fieldnames:
                raise SystemExit(f"MISSING_REQUIRED_COLUMN {col}")

        for row in reader:
            rows.append({
                "bin_start": parse_int(row, "bin_start"),
                "bin_end": parse_int(row, "bin_end"),
                "localization_class": get_text(row, "localization_class"),
            })

    rows.sort(key=lambda r: (r["bin_start"], r["bin_end"]))

    out_rows = []
    current = []
    candidate_idx = 1

    for row in rows:
        cls = row["localization_class"]

        if cls in ACTIVE_CLASSES:
            current.append(row)
            continue

        if current:
            out_rows.append(emit_candidate(args, candidate_idx, current))
            candidate_idx += 1
            current = []

    if current:
        out_rows.append(emit_candidate(args, candidate_idx, current))

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
