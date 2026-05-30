import argparse
from pathlib import Path

def read_fasta(path):
    parts = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        parts.append(line.upper())
    return "".join(parts)

def band(value):
    if value < 0.25:
        return "low"
    if value < 0.45:
        return "mid_low"
    if value < 0.55:
        return "mid"
    if value < 0.75:
        return "mid_high"
    return "high"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fasta", required=True)
    p.add_argument("--out-log", required=True)
    p.add_argument("--chunk", type=int, default=60)
    p.add_argument("--step", type=int, default=20)
    args = p.parse_args()

    seq = read_fasta(args.fasta)
    out = Path(args.out_log)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    for start in range(0, max(0, len(seq) - args.chunk + 1), args.step):
        chunk = seq[start:start + args.chunk]
        n = max(1, len(chunk))

        a = chunk.count("A") / n
        c = chunk.count("C") / n
        g = chunk.count("G") / n
        t = chunk.count("T") / n
        gc = (chunk.count("G") + chunk.count("C")) / n
        at = (chunk.count("A") + chunk.count("T")) / n

        cg_count = chunk.count("CG")
        ta_count = chunk.count("TA")
        repeat_score = max(
            chunk.count("AAAA"),
            chunk.count("TTTT"),
            chunk.count("CCCC"),
            chunk.count("GGGG")
        )

        rows.append(
            "dna"
            + " pos=" + str(start + 1)
            + " chunk=" + str(args.chunk)
            + " gc=" + band(gc)
            + " at=" + band(at)
            + " a=" + band(a)
            + " c=" + band(c)
            + " g=" + band(g)
            + " t=" + band(t)
            + " cg=" + ("present" if cg_count > 0 else "absent")
            + " ta=" + ("present" if ta_count > 0 else "absent")
            + " repeat=" + ("high" if repeat_score >= 2 else "low")
        )

    out.write_text("\n".join(rows), encoding="utf-8")
    print("WROTE", out.resolve(), "rows", len(rows))

if __name__ == "__main__":
    main()
