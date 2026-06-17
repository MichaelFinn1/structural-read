import argparse
import csv
import re
from pathlib import Path
from collections import Counter

def family_for_line(line: str) -> str:
    s = line.strip().lower()

    s = re.sub(r"\b\d{4}-\d{2}-\d{2}[t_ ]\d{2}:\d{2}:\d{2}(?:\.\d+)?z?\b", "<ts>", s)
    s = re.sub(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", "<ip>", s)
    s = re.sub(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "<uuid>", s)
    s = re.sub(r"\b0x[0-9a-f]+\b", "<hex>", s)
    protected = []

    def protect_numeric_bin(m):
        protected.append(m.group(0))
        return f"__PROTECTED_NUMERIC_BIN_{len(protected)-1}__"

    s = re.sub(r"\b(?:amp_q|delta_q)=-?\d+\b", protect_numeric_bin, s)
    s = re.sub(r"\b-?\d+\b", "<num>", s)

    for i, value in enumerate(protected):
        s = s.replace(f"__PROTECTED_NUMERIC_BIN_{i}__", value)
    s = re.sub(r"\s+", " ", s)

    parts = s.split()
    return " ".join(parts[:8]) if parts else "<blank>"

def classify_window(lines):
    families = [family_for_line(x) for x in lines]
    counts = Counter(families)

    stable = 0
    middle = 0
    residual = 0

    for fam in families:
        c = counts[fam]
        if c >= 4:
            stable += 1
        elif c >= 2:
            middle += 1
        else:
            residual += 1

    n = max(1, len(lines))
    dominant_family, dominant_count = counts.most_common(1)[0] if counts else ("<none>", 0)

    return {
        "stable_lines": stable,
        "middle_lines": middle,
        "residual_lines": residual,
        "stable_share": stable / n,
        "middle_share": middle / n,
        "residual_share": residual / n,
        "dominant_residual_family": dominant_family,
        "dominant_residual_family_share": dominant_count / n,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-log", required=True)
    parser.add_argument("--out-csv", required=True)
    parser.add_argument("--window-sizes", default="50,75,100,150,200,250,350,500,750,1000")
    args = parser.parse_args()

    raw_path = Path(args.raw_log)
    out_path = Path(args.out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = raw_path.read_text(encoding="utf-8", errors="replace").splitlines()
    sizes = [int(x.strip()) for x in args.window_sizes.split(",") if x.strip()]

    fields = [
        "window_size","window_id","line_start","line_end","lines",
        "stable_lines","middle_lines","residual_lines",
        "stable_share","middle_share","residual_share",
        "residual_self_adjacent","residual_near_stable","residual_near_middle",
        "residual_self_adjacent_share","residual_near_stable_share",
        "dominant_residual_family_share","dominant_residual_family",
        "local_residue_posture"
    ]

    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()

        for size in sizes:
            window_id = 0
            for start_idx in range(0, len(lines), size):
                chunk = lines[start_idx:start_idx + size]
                if not chunk:
                    continue

                window_id += 1
                c = classify_window(chunk)

                row = {
                    "window_size": size,
                    "window_id": window_id,
                    "line_start": start_idx + 1,
                    "line_end": start_idx + len(chunk),
                    "lines": len(chunk),
                    **c,
                    "residual_self_adjacent": "",
                    "residual_near_stable": "",
                    "residual_near_middle": "",
                    "residual_self_adjacent_share": "",
                    "residual_near_stable_share": "",
                    "local_residue_posture": "generic"
                }
                w.writerow(row)

    print("WROTE", out_path.resolve())

if __name__ == "__main__":
    main()

