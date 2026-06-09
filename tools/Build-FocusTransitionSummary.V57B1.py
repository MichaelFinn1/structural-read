#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
from collections import Counter


OUT_FIELDS = [
    "terrain",
    "total_transitions",
    "persisted_count",
    "persisted_share",
    "smoothed_count",
    "smoothed_share",
    "fragmented_count",
    "fragmented_share",
    "dominant_posture_transition",
    "dominant_posture_transition_share",
    "deformation_profile",
]


def read_named_inputs(path_text):
    items = []
    for raw in path_text:
        raw = raw.strip()
        if not raw:
            continue
        if "=" not in raw:
            raise SystemExit("BAD_INPUT_EXPECTED terrain=path")
        name, file_path = raw.split("=", 1)
        name = name.strip()
        file_path = file_path.strip()
        if not name or not file_path:
            raise SystemExit("BAD_INPUT_EXPECTED terrain=path")
        items.append((name, Path(file_path)))
    return items


def share(count, total):
    if total <= 0:
        return "0.0000"
    return f"{count / total:.4f}"


def profile(markers, postures, total):
    if total <= 0:
        return "empty"

    persisted = markers.get("persisted", 0)
    smoothed = markers.get("smoothed", 0)
    fragmented = markers.get("fragmented", 0)

    persisted_share = persisted / total
    smoothed_share = smoothed / total
    fragmented_share = fragmented / total

    dominant_posture, dominant_count = postures.most_common(1)[0]
    dominant_posture_share = dominant_count / total

    if persisted_share == 1.0:
        return "total_persistence"

    if persisted_share >= 0.85:
        if smoothed > 0 and fragmented == 0:
            return "persistence_dominant_smoothed_tail"
        if fragmented > 0 and smoothed == 0:
            return "persistence_dominant_fragmented_tail"
        if smoothed > 0 and fragmented > 0:
            if abs(smoothed_share - fragmented_share) <= 0.01:
                return "persistence_dominant_balanced_tail"
            if smoothed_share > fragmented_share:
                return "persistence_dominant_smoothed_tail"
            return "persistence_dominant_fragmented_tail"

    if dominant_posture == "residual, residual" and dominant_posture_share >= 0.50:
        return "residual_persistence_dominant"

    if dominant_posture == "stable, stable" and dominant_posture_share >= 0.50:
        return "stable_persistence_dominant"

    return "mixed_transition_tail"


def summarize(name, file_path):
    if not file_path.exists():
        raise SystemExit(f"MISSING_INPUT {file_path}")

    markers = Counter()
    postures = Counter()
    total = 0

    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = ["transition_marker", "from_posture", "to_posture"]
        for col in required:
            if col not in reader.fieldnames:
                raise SystemExit(f"MISSING_REQUIRED_COLUMN {col} in {file_path}")

        for row in reader:
            total += 1
            marker = row["transition_marker"]
            posture = f"{row['from_posture']}, {row['to_posture']}"
            markers[marker] += 1
            postures[posture] += 1

    if total == 0:
        dominant_posture = ""
        dominant_posture_share = "0.0000"
    else:
        dominant_posture, dominant_count = postures.most_common(1)[0]
        dominant_posture_share = share(dominant_count, total)

    persisted = markers.get("persisted", 0)
    smoothed = markers.get("smoothed", 0)
    fragmented = markers.get("fragmented", 0)

    return {
        "terrain": name,
        "total_transitions": total,
        "persisted_count": persisted,
        "persisted_share": share(persisted, total),
        "smoothed_count": smoothed,
        "smoothed_share": share(smoothed, total),
        "fragmented_count": fragmented,
        "fragmented_share": share(fragmented, total),
        "dominant_posture_transition": dominant_posture,
        "dominant_posture_transition_share": dominant_posture_share,
        "deformation_profile": profile(markers, postures, total),
    }


def main():
    ap = argparse.ArgumentParser(
        description="Build observer-only terrain-level focus transition summary."
    )
    ap.add_argument(
        "--input",
        action="append",
        required=True,
        help="Named input in the form terrain=path_to_focus_transition_surface_v0.csv",
    )
    ap.add_argument("--out-csv", required=True)
    args = ap.parse_args()

    items = read_named_inputs(args.input)
    rows = [summarize(name, path) for name, path in items]

    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    tmp_path.replace(out_path)
    print(f"WROTE {out_path}")
    print(f"ROWS {len(rows)}")


if __name__ == "__main__":
    main()
