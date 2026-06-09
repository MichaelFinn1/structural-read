#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


OUT_FIELDS = [
    "terrain_id",
    "from_focus_size",
    "to_focus_size",
    "from_line_start",
    "from_line_end",
    "to_line_start",
    "to_line_end",
    "overlap_ratio",
    "from_posture",
    "to_posture",
    "from_legibility",
    "to_legibility",
    "delta_stable",
    "delta_middle",
    "delta_residual",
    "transition_marker",
]


def parse_int(row, name):
    try:
        return int(row[name])
    except KeyError:
        raise SystemExit(f"MISSING_REQUIRED_COLUMN {name}")
    except ValueError:
        raise SystemExit(f"BAD_INT {name}={row.get(name)}")


def parse_float(row, name):
    try:
        return float(row[name])
    except KeyError:
        raise SystemExit(f"MISSING_REQUIRED_COLUMN {name}")
    except ValueError:
        raise SystemExit(f"BAD_FLOAT {name}={row.get(name)}")


def get_text(row, name):
    if name not in row:
        raise SystemExit(f"MISSING_REQUIRED_COLUMN {name}")
    return row[name]


def overlap_len(a_start, a_end, b_start, b_end):
    start = max(a_start, b_start)
    end = min(a_end, b_end)
    if end < start:
        return 0
    return end - start + 1


def marker(from_posture, to_posture, from_mix, to_mix):
    if from_posture == to_posture:
        return "persisted"

    if from_posture == "residual" and to_posture in ("middle", "stable"):
        return "smoothed"

    if from_posture == "middle" and to_posture == "stable":
        return "smoothed"

    if from_posture == "stable" and to_posture in ("middle", "residual"):
        return "fragmented"

    if from_posture == "middle" and to_posture == "residual":
        return "fragmented"

    if from_mix is not None and to_mix is not None:
        if from_mix - to_mix >= 2:
            return "recomposed"

    return "posture_changed"


def maybe_mix(row):
    value = row.get("posture_mix_count", "")
    if value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser(
        description="Build observer-only focus transition surface from focus ladder surface."
    )
    ap.add_argument("--terrain-id", required=True)
    ap.add_argument("--ladder-csv", required=True)
    ap.add_argument("--out-csv", required=True)
    args = ap.parse_args()

    ladder_path = Path(args.ladder_csv)
    out_path = Path(args.out_csv)

    rows = []
    with ladder_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_focus_size"] = parse_int(row, "focus_size")
            row["_line_start"] = parse_int(row, "line_start")
            row["_line_end"] = parse_int(row, "line_end")
            row["_stable_share"] = parse_float(row, "stable_share")
            row["_middle_share"] = parse_float(row, "middle_share")
            row["_residual_share"] = parse_float(row, "residual_share")
            row["_dominant_posture"] = get_text(row, "dominant_posture")
            row["_legibility_class"] = get_text(row, "legibility_class")
            row["_posture_mix_count"] = maybe_mix(row)
            rows.append(row)

    by_focus = {}
    for row in rows:
        by_focus.setdefault(row["_focus_size"], []).append(row)

    focus_sizes = sorted(by_focus.keys())
    out_rows = []

    for i in range(len(focus_sizes) - 1):
        from_size = focus_sizes[i]
        to_size = focus_sizes[i + 1]

        from_rows = by_focus[from_size]
        to_rows = by_focus[to_size]

        for fr in from_rows:
            fr_start = fr["_line_start"]
            fr_end = fr["_line_end"]
            fr_len = fr_end - fr_start + 1

            best = None
            best_ratio = 0.0

            for tr in to_rows:
                tr_start = tr["_line_start"]
                tr_end = tr["_line_end"]
                tr_len = tr_end - tr_start + 1

                ov = overlap_len(fr_start, fr_end, tr_start, tr_end)
                if ov <= 0:
                    continue

                denom = min(fr_len, tr_len)
                ratio = ov / denom

                if ratio > best_ratio:
                    best = tr
                    best_ratio = ratio

            if best is None or best_ratio < 0.50:
                continue

            from_posture = fr["_dominant_posture"]
            to_posture = best["_dominant_posture"]

            delta_stable = best["_stable_share"] - fr["_stable_share"]
            delta_middle = best["_middle_share"] - fr["_middle_share"]
            delta_residual = best["_residual_share"] - fr["_residual_share"]

            out_rows.append({
                "terrain_id": args.terrain_id,
                "from_focus_size": from_size,
                "to_focus_size": to_size,
                "from_line_start": fr_start,
                "from_line_end": fr_end,
                "to_line_start": best["_line_start"],
                "to_line_end": best["_line_end"],
                "overlap_ratio": f"{best_ratio:.4f}",
                "from_posture": from_posture,
                "to_posture": to_posture,
                "from_legibility": fr["_legibility_class"],
                "to_legibility": best["_legibility_class"],
                "delta_stable": f"{delta_stable:.4f}",
                "delta_middle": f"{delta_middle:.4f}",
                "delta_residual": f"{delta_residual:.4f}",
                "transition_marker": marker(
                    from_posture,
                    to_posture,
                    fr["_posture_mix_count"],
                    best["_posture_mix_count"],
                ),
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        writer.writeheader()
        writer.writerows(out_rows)

    tmp_path.replace(out_path)
    print(f"WROTE {out_path}")


if __name__ == "__main__":
    main()
