import argparse
import csv
from pathlib import Path


REQUIRED_COLUMNS = [
    "window_size",
    "line_start",
    "line_end",
    "stable_share",
    "middle_share",
    "residual_share",
]


OUTPUT_FIELDS = [
    "terrain_id",
    "focus_size",
    "window_id",
    "line_start",
    "line_end",
    "stable_share",
    "middle_share",
    "residual_share",
    "dominant_posture",
    "seam_count",
    "posture_mix_count",
    "legibility_class",
    "band_sequence",
]


def parse_focus_sizes(text):
    out = []
    for part in text.split(","):
        value = part.strip()
        if value:
            out.append(int(value))
    return out


def as_float(value):
    return float(str(value).strip())


def dominant_posture(row):
    values = {
        "stable": as_float(row["stable_share"]),
        "middle": as_float(row["middle_share"]),
        "residual": as_float(row["residual_share"]),
    }
    return max(values, key=values.get)


def posture_initial(posture):
    if posture == "stable":
        return "S"
    if posture == "middle":
        return "M"
    if posture == "residual":
        return "R"
    return "?"


def posture_mix_count(row):
    n = 0
    for key in ["stable_share", "middle_share", "residual_share"]:
        if as_float(row[key]) > 0.05:
            n += 1
    return n


def legibility_class(row, mix_count):
    stable = as_float(row["stable_share"])
    middle = as_float(row["middle_share"])
    residual = as_float(row["residual_share"])

    if stable >= 0.60:
        return "dominant_stable"
    if middle >= 0.60:
        return "dominant_middle"
    if residual >= 0.60:
        return "dominant_residual"
    if mix_count >= 2:
        return "mixed"
    return "unresolved"


def seam_count_for_sequence(postures):
    count = 0
    prev = None

    for posture in postures:
        if prev is not None and posture != prev:
            count += 1
        prev = posture

    return count


def main():
    parser = argparse.ArgumentParser(
        description="Build focus_ladder_surface_v0.csv from traversal-window CSV."
    )

    parser.add_argument("--terrain-id", required=True)
    parser.add_argument("--windows-csv", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--focus-sizes", required=True)

    args = parser.parse_args()

    terrain_id = args.terrain_id
    windows_csv = Path(args.windows_csv)
    out_csv = Path(args.out_csv)
    focus_sizes = parse_focus_sizes(args.focus_sizes)

    rows = list(csv.DictReader(windows_csv.open("r", encoding="utf-8")))

    if not rows:
        raise RuntimeError("Input CSV has no rows.")

    header = rows[0].keys()
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in header]

    if missing_columns:
        raise RuntimeError(
            "Missing required columns: " + ", ".join(missing_columns)
        )

    by_size = {}

    for row in rows:
        size = int(float(row["window_size"]))
        if size not in focus_sizes:
            continue

        by_size.setdefault(size, []).append(row)

    missing_sizes = [s for s in focus_sizes if s not in by_size]

    if missing_sizes:
        print("MISSING_FOCUS_SIZES " + ",".join(str(x) for x in missing_sizes))

    output_rows = []

    for size in focus_sizes:
        size_rows = by_size.get(size, [])
        if not size_rows:
            continue

        size_rows.sort(
            key=lambda r: (
                int(float(r["line_start"])),
                int(float(r["line_end"])),
            )
        )

        postures = [dominant_posture(r) for r in size_rows]
        band_sequence = "".join(posture_initial(p) for p in postures)
        seam_count = seam_count_for_sequence(postures)

        for idx, row in enumerate(size_rows, start=1):
            posture = postures[idx - 1]
            mix_count = posture_mix_count(row)
            legibility = legibility_class(row, mix_count)

            output_rows.append({
                "terrain_id": terrain_id,
                "focus_size": size,
                "window_id": idx,
                "line_start": int(float(row["line_start"])),
                "line_end": int(float(row["line_end"])),
                "stable_share": row["stable_share"],
                "middle_share": row["middle_share"],
                "residual_share": row["residual_share"],
                "dominant_posture": posture,
                "seam_count": seam_count,
                "posture_mix_count": mix_count,
                "legibility_class": legibility,
                "band_sequence": band_sequence,
            })

    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    print("WROTE " + str(out_csv.resolve()))
    print("ROWS " + str(len(output_rows)))


if __name__ == "__main__":
    main()
