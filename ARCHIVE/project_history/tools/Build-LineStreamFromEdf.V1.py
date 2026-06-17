import argparse
import struct
from pathlib import Path

def read_ascii(b):
    return b.decode("ascii", errors="ignore").strip()

def qbin(x, scale=10, lo=-30, hi=30):
    v = int(round(x * scale))
    return max(lo, min(hi, v))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--edf", required=True)
    p.add_argument("--out-log", required=True)
    p.add_argument("--channel", type=int, default=0)
    p.add_argument("--max-samples", type=int, default=20000)
    args = p.parse_args()

    data = Path(args.edf).read_bytes()

    header_bytes = int(read_ascii(data[184:192]))
    signal_count = int(read_ascii(data[252:256]))
    off = 256

    labels = [read_ascii(data[off+i*16:off+(i+1)*16]) for i in range(signal_count)]
    off += 16 * signal_count
    off += 80 * signal_count
    off += 8 * signal_count

    phys_min = [float(read_ascii(data[off+i*8:off+(i+1)*8])) for i in range(signal_count)]
    off += 8 * signal_count
    phys_max = [float(read_ascii(data[off+i*8:off+(i+1)*8])) for i in range(signal_count)]
    off += 8 * signal_count
    dig_min = [float(read_ascii(data[off+i*8:off+(i+1)*8])) for i in range(signal_count)]
    off += 8 * signal_count
    dig_max = [float(read_ascii(data[off+i*8:off+(i+1)*8])) for i in range(signal_count)]
    off += 8 * signal_count

    off += 80 * signal_count

    samples_per_record = [int(read_ascii(data[off+i*8:off+(i+1)*8])) for i in range(signal_count)]

    record_size_samples = sum(samples_per_record)
    record_size_bytes = record_size_samples * 2
    records = (len(data) - header_bytes) // record_size_bytes

    ch = args.channel
    label = (labels[ch] or ("channel_" + str(ch))).replace(" ", "_")

    values = []
    ptr = header_bytes

    for r in range(records):
        sig_ptr = ptr
        for s in range(signal_count):
            count = samples_per_record[s]
            if s == ch:
                for j in range(count):
                    raw = struct.unpack_from("<h", data, sig_ptr + j * 2)[0]
                    scale = (phys_max[s] - phys_min[s]) / max(1.0, (dig_max[s] - dig_min[s]))
                    phys = phys_min[s] + (raw - dig_min[s]) * scale
                    values.append(phys)
                    if len(values) >= args.max_samples:
                        break
            sig_ptr += count * 2
            if len(values) >= args.max_samples:
                break
        ptr += record_size_bytes
        if len(values) >= args.max_samples:
            break

    mean = sum(values) / len(values)
    var = sum((x - mean) ** 2 for x in values) / max(1, len(values) - 1)
    sd = var ** 0.5 if var > 0 else 1.0

    rows = []
    prev_z = 0.0

    for i, v in enumerate(values, start=1):
        z = (v - mean) / sd
        dz = z - prev_z
        prev_z = z

        rows.append(
            "eeg"
            + " channel=" + label
            + " amp_q=" + str(qbin(z, scale=8))
            + " delta_q=" + str(qbin(dz, scale=16))
            + " phase=" + ("pos" if z >= 0 else "neg")
        )

    out = Path(args.out_log)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(rows), encoding="utf-8")

    print("WROTE", out.resolve(), "rows", len(rows), "channel", ch, label)

if __name__ == "__main__":
    main()
