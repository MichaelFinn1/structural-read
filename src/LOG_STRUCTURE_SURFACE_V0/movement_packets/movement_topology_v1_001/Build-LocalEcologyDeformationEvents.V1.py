import csv
from pathlib import Path

SRC = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/middle_feature_relation_read_v1.csv")
OUT = Path("src/LOG_STRUCTURE_SURFACE_V0/movement_packets/movement_topology_v1_001/local_ecology_deformation_events_v1.csv")

def zone_for_interval(interval_text):
    if not interval_text:
        return "none"

    start = int(interval_text.split("-")[0])
    end = int(interval_text.split("-")[1])
    center = (start + end) / 2

    if center <= 750:
        return "left_zone"
    if center <= 1250:
        return "null_zone"
    return "right_zone"

def width(interval_text):
    if not interval_text:
        return 0
    start = int(interval_text.split("-")[0])
    end = int(interval_text.split("-")[1])
    return end - start + 1

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))

events = []

for r in rows:
    from_interval = r["from_interval"]
    to_interval = r["to_interval"]

    from_width = width(from_interval)
    to_width = width(to_interval)

    from_zone = zone_for_interval(from_interval)
    to_zone = zone_for_interval(to_interval)

    center_delta = r["center_delta"]

    if center_delta == "":
        direction = "none"
    else:
        delta = float(center_delta)
        if delta > 0:
            direction = "rightward"
        elif delta < 0:
            direction = "leftward"
        else:
            direction = "held"

    width_delta = to_width - from_width

    if width_delta > 0:
        width_change = "widens"
    elif width_delta < 0:
        width_change = "thins"
    else:
        width_change = "preserves_width"

    if from_width > 0 and to_width > 0:
        preservation_ratio = round(to_width / from_width, 3)
    else:
        preservation_ratio = ""

    if r["relation_type"] in ["merges", "splits"]:
        mass_note = "check_width_preservation"
    elif r["relation_type"] == "continues" and abs(width_delta) <= 5:
        mass_note = "width_preserved"
    elif r["relation_type"] == "disappears":
        mass_note = "fade_or_drop"
    elif r["relation_type"] == "appears":
        mass_note = "appearance_or_reconstitution"
    else:
        mass_note = "ordinary_deformation"

    events.append({
        "from_window_size": r["from_window_size"],
        "to_window_size": r["to_window_size"],
        "from_zone": from_zone,
        "to_zone": to_zone,
        "from_interval": from_interval,
        "to_interval": to_interval,
        "from_width": from_width,
        "to_width": to_width,
        "width_delta": width_delta,
        "width_preservation_ratio": preservation_ratio,
        "direction": direction,
        "relation_type": r["relation_type"],
        "overlap_lines": r["overlap_lines"],
        "event_note": mass_note,
        "boundary": "deformation_event_not_identity_or_semantics"
    })

fields = list(events[0].keys())

with OUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(events)

print("")
print("WROTE")
print(OUT.resolve())
print("")
