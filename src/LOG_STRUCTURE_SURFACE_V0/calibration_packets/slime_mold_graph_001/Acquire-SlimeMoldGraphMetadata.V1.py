import json
import urllib.request
from pathlib import Path

PACKET = Path("src/LOG_STRUCTURE_SURFACE_V0/calibration_packets/slime_mold_graph_001")
RAW = PACKET / "raw"
RAW.mkdir(parents=True, exist_ok=True)

META_URL = "https://edmond.mpg.de/api/datasets/export?exporter=dataverse_json&persistentId=doi:10.17617/3.XWST2Q"

meta_path = RAW / "slime_mold_graph_repository_metadata.json"

urllib.request.urlretrieve(META_URL, meta_path)

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
    if any(ext in name for ext in [".graphml", ".gml", ".gexf", ".xml", ".zip"]):
        candidates.append(f)

candidates = sorted(candidates, key=lambda r: int(r["size"] or 0))

out = RAW / "candidate_graph_files.csv"
with out.open("w", encoding="utf-8") as fh:
    fh.write("id,filename,size,content_type\n")
    for f in candidates[:80]:
        fh.write(f'{f["id"]},"{f["filename"]}",{f["size"]},"{f["content_type"]}"\n')

print("WROTE", meta_path.resolve())
print("WROTE", out.resolve())
print("CANDIDATES", len(candidates))

if candidates:
    chosen = candidates[0]
    file_id = chosen["id"]
    filename = chosen["filename"]
    url = f"https://edmond.mpg.de/api/access/datafile/{file_id}"
    dest = RAW / filename

    urllib.request.urlretrieve(url, dest)

    print("DOWNLOADED", dest.resolve())
    print("CHOSEN_ID", file_id)
    print("CHOSEN_FILE", filename)
else:
    print("NO_GRAPH_FILE_CANDIDATES_FOUND")
