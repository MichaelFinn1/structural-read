import argparse
from pathlib import Path

def read_fasta(path):
    lines = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(">"):
            continue
        lines.append(line.strip().upper())
    return "".join(lines)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--fasta", required=True)
    p.add_argument("--out-log", required=True)
    p.add_argument("--k", type=int, default=12)
    p.add_argument("--step", type=int, default=1)
    args = p.parse_args()

    seq = read_fasta(args.fasta)
    out = Path(args.out_log)
    out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for i in range(0, max(0, len(seq) - args.k + 1), args.step):
        kmer = seq[i:i + args.k]
        gc = (kmer.count("G") + kmer.count("C")) / max(1, len(kmer))
        rows.append(f"dna pos={i+1} kmer={kmer} gc_band={round(gc, 2)}")

    out.write_text("\n".join(rows), encoding="utf-8")
    print("WROTE", out.resolve(), "rows", len(rows))

if __name__ == "__main__":
    main()
