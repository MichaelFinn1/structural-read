import json
import urllib.request
from pathlib import Path

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/slime_mold_graph_001")
RAW = PACKET / "raw"

meta_path = RAW / "slime_mold_graph_repository_metadata.json"
data = json.loads(meta_path.read_text(encoding="utf-8"))

files = []

def walk(x):
    if isinstance(x, dict):
        if "dataFile" in x:
            df = x["dataFile"]
            files.append({
                "id": df.get("id"),
                "filename": df.get("filename", ""),
                "size": df.get("filesize", 0),
                "content_type": df.get("contentType", ""),
            })
        for v in x.values():
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)

walk(data)

candidates = []
for f in files:
    name = f["filename"].lower()
    if any(ext in name for ext in [".graphml", ".gml", ".gexf", ".xml", ".zip", ".csv", ".txt"]):
        candidates.append(f)

candidates = sorted(candidates, key=lambda r: int(r["size"] or 0))

out = RAW / "candidate_graph_files.csv"
with out.open("w", encoding="utf-8") as fh:
    fh.write("id,filename,size,content_type\n")
    for f in candidates[:100]:
        fh.write(f'{f["id"]},"{f["filename"]}",{f["size"]},"{f["content_type"]}"\n')

print("WROTE", out.resolve())
print("CANDIDATES", len(candidates))
