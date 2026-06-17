import csv
import json
import argparse
from pathlib import Path

BASE = Path(__file__).resolve().parent

parser = argparse.ArgumentParser()

parser.add_argument(
    "--structure-csv",
    required=True
)

parser.add_argument(
    "--raw-log",
    required=True
)

parser.add_argument(
    "--out-html",
    required=True
)

args = parser.parse_args()

SRC = Path(args.structure_csv)
RAW = Path(args.raw_log)
OUT = Path(args.out_html)


# ============================================================
# SECTION 1 — DATA LOAD
# ============================================================

rows = list(csv.DictReader(SRC.open("r", encoding="utf-8")))
for r in rows:
    for k in ["window_size","line_start","line_end","stable_share","middle_share","residual_share"]:
        r[k] = float(r[k])

sizes = sorted(set(int(r["window_size"]) for r in rows))
max_line = max(int(r["line_end"]) for r in rows)

source_lines = RAW.read_text(
    encoding="utf-8",
    errors="replace"
).splitlines()

payload = {"rows": rows, "sizes": sizes, "max_line": max_line, "source_lines": source_lines}
payload_json = json.dumps(payload)

html = f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Global Focus Lens</title>
<style>
.rawLogRow {{
  display: block;
  opacity: 1;
  font-family: Consolas, monospace;
  font-size: 13px;
  margin-bottom: 2px;
}}

.rawIncludeBox {{
  margin-right: 6px;
}}

.rawLineNumber {{
  color: #444;
}}

.rawLineText {{
  color: black;
}}

.rawSuffix {{
  margin-top: 10px;
  color: #666;
  font-family: Consolas, monospace;
  font-size: 12px;
}}

.rawLogRow.excluded {{
  opacity: 0.42;
}}
.microExcluded {{ background: #cc2b2b; }}

body {{ font-family: Georgia, serif; margin: 26px; background: white; }}
h1 {{ text-align: center; font-weight: normal; }}
#wrap {{ width: 96%; margin: 0 auto; }}
.controls {{ display:none; }}

.lensSizeBox {{
  display:none;
}}

.lensProfileRow {{
  display:grid;
  grid-template-columns:72px 1fr;
  gap:10px;
  align-items:stretch;
  margin-top:14px;
}}

.lensProfile {{
  position:relative;
  border:1px solid #777;
  background:#fafafa;
  height:100%;
  min-height:70px;
  user-select:none;
  cursor:ns-resize;
  overflow:hidden;
}}

.lensProfileValue {{
  position:absolute;
  top:2px;
  right:4px;
  font-family:Consolas, monospace;
  font-size:11px;
  background:white;
  border:1px solid #aaa;
  padding:1px 4px;
  z-index:5;
}}

.lensProfileStep {{
  position:absolute;
  left:0;
  right:0;
  height:2px;
}}

.lensProfileMark {{
  position:absolute;
  left:7px;
  top:50%;
  transform:translateY(-50%);
  height:2px;
  border-radius:2px;
  opacity:0.35;
  background:#444;
}}

.lensProfileStep.active .lensProfileMark {{
  height:7px;
  opacity:1;
  background:#1f66d1;
  box-shadow:0 0 4px rgba(31,102,209,0.55);
}}

#focusLensProfile .lensProfileStep.active .lensProfileMark {{
  background:#188a3a;
  box-shadow:0 0 4px rgba(24,138,58,0.55);
}}
.box {{ border: 1px solid #aaa; padding: 12px; }}
input[type=range] {{ width: 100%; }}
.label {{ text-align: center; font-size: 18px; margin: 10px; }}
.bar {{ position: relative; height: 78px; border: 1px solid black; margin-top: 14px; display: flex; overflow: visible; user-select: none; }}
.focusBar {{ height: 145px; cursor: crosshair; }}
.seg {{ height: 100%; }}
.stable {{ background: white; }}
.middle {{ background: #bfbfbf; }}
.residual {{ background: #222222; }}
.lens {{
  position: absolute;
  top: 0;
  height: 100%;
  border-left: 3px solid red;
  border-right: 3px solid red;
  background: rgba(47,95,143,0.14);
  pointer-events: auto;
  z-index: 900;
}}

.lensHandle {{
  position:absolute;
  pointer-events:auto;
  background:#2f5f8f;
  border:1px solid #17344f;
  z-index:1400;
}}

.lensMoveHandle {{
  left:50%;
  bottom:-15px;
  width:46px;
  height:11px;
  transform:translateX(-50%);
  cursor:grab;
}}

.lensResizeLeft {{
  left:-14px;
  top:34%;
  width:11px;
  height:32%;
  cursor:ew-resize;
}}

.lensResizeRight {{
  right:-14px;
  top:34%;
  width:11px;
  height:32%;
  cursor:ew-resize;
}}
.dragBox {{ position: absolute; top: 0; height: 100%; background: rgba(255,0,0,0.18); border-left: 2px dashed red; border-right: 2px dashed red; pointer-events: none; }}
.legend {{ text-align: center; margin-top: 18px; font-size: 15px; }}
.note {{ margin-top: 22px; font-size: 16px; line-height: 1.4; }}
#linePreview {{ border:1px solid #999; padding:12px; height:240px; overflow:auto; white-space:pre-wrap; font-family:Consolas, monospace; font-size:13px; }}


.microBarLabel {{
  font-size: 12px;
  font-family: Consolas, monospace;
  margin: 3px 0;
}}

.microBar {{
  display: flex;
  height: 14px;
  border: 1px solid #999;
  margin-bottom: 4px;
  overflow: hidden;
  user-select: none;
}}

.microBlock {{
  flex: 1 1 0;
  min-width: 1px;
  height: 100%;
}}

.microStable {{ background: #ffffff; }}
.microMiddle {{ background: #bfbfbf; }}
.microResidual {{ background: #222222; }}
.microIncluded {{ background: #208f3a; }}
.microExcluded {{ background: #cc2b2b; }}

.focusRangeFrame {{
  position:absolute;
  top:0;
  height:100%;
  box-sizing:border-box;
  pointer-events:none;
}}

.basinFrame {{
  border-left:6px solid #8a5a2b;
  border-right:6px solid #8a5a2b;
  border-top:3px solid #8a5a2b;
  border-bottom:3px solid #8a5a2b;
  background:rgba(138,90,43,0.12);
  z-index:55;
  pointer-events:auto;
}}

.inspectionFrame {{
  border-left:3px solid #188a3a;
  border-right:3px solid #188a3a;
  border-top:2px solid #188a3a;
  border-bottom:2px solid #188a3a;
  background:rgba(24,138,58,0.10);
  z-index:45;
  pointer-events:auto;
}}

.apertureFrame {{
  border-left:2px solid #2f6f9f;
  border-right:2px solid #2f6f9f;
  border-top:1px solid #2f6f9f;
  border-bottom:1px solid #2f6f9f;
  background:rgba(120,190,235,0.22);
  z-index:60;
  pointer-events:none;
}}


.focusRangeFrame.apertureFrame {{
  border-left: 8px solid #ff3300 !important;
  border-right: 8px solid #ff3300 !important;
  background: rgba(255, 51, 0, 0.45) !important;
  z-index: 999 !important;
  box-shadow: inset 0 0 0 3px #ff3300, 0 0 10px rgba(255,51,0,0.95);
}}
.framePointLabel {{
  position:absolute;
  font-family:Consolas, monospace;
  font-size:11px;
  background:white;
  border:1px solid #777;
  padding:1px 5px;
  z-index:50;
  white-space:nowrap;
}}

.framePointLabel.mid {{
  top:-34px;
  left:50%;
  transform:translateX(-50%);
}}

.framePointLabel.left {{
  top:-18px;
  left:0;
  transform:translateX(-50%);
}}

.framePointLabel.right {{
  top:-18px;
  right:0;
  transform:translateX(50%);
}}


#bookmarkCards {{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:12px;
}}

.bookmarkCard {{
  border:1px solid #999;
  padding:8px;
  width:220px;
  cursor:pointer;
  background:#fafafa;
  font-family:Consolas, monospace;
  font-size:12px;
}}

.bookmarkCard:hover {{
  background:#f0f0f0;
}}


#lowerWorkbench {{
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 14px;
  align-items: start;
  margin-top: 12px;
}}

#lowerLeftPanel,
#lowerRightPanel {{
  border: 1px solid #bbb;
  background: #fafafa;
  padding: 10px;
}}

#selectionPad {{
  display: grid;
  grid-template-columns: 70px 58px;
  grid-template-rows: 34px 34px 34px;
  gap: 6px;
  align-items: stretch;
  margin-bottom: 12px;
}}

#selectionPad button {{
  font-size: 12px !important;
  border: 1px solid #777;
  cursor: pointer;
}}

#selectAllFocus {{
  grid-row: 1 / span 3;
  width: 70px;
  font-weight: bold;
}}

#selectWhiteFocus {{
  background: #fff;
}}

#selectGreyFocus {{
  background: #bfbfbf;
}}

#selectBlackFocus {{
  background: #222;
  color: white;
}}

.csvControlGroup {{
  border-top: 1px solid #ccc;
  padding-top: 10px;
  margin-top: 10px;
}}

.csvTitle {{
  font-family: Consolas, monospace;
  font-size: 13px;
  font-weight: bold;
  margin-bottom: 6px;
}}

.csvSaveRow,
.csvActionRow {{
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 7px;
}}

.csvBrownButton {{
  border: 2px solid #8a5a2b;
  background: #f4eadf;
}}

.csvGreenButton {{
  border: 2px solid #188a3a;
  background: #e7f6ea;
}}

.csvFocusButton {{
  border: 2px solid #5da9e9;
  background: #eaf5fd;
}}

#csvSelectionControls {{
  border: 0 !important;
  background: transparent !important;
  padding: 0 !important;
  margin: 0 0 10px 0 !important;
}}

#csvPacketSurface {{
  margin-top: 10px !important;
}}

#linePreview {{
  width: 100%;
  box-sizing: border-box;
}}

#lowerRightPanel .stickyNoteBox {{
  margin-top: 12px;
}}


#projectionLayer {{
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 2;
}}

.lens .lensResizeLeft {{
  top: auto !important;
  bottom: -16px !important;
  left: -6px !important;
}}

.lens .lensResizeRight {{
  top: auto !important;
  bottom: -16px !important;
  right: -6px !important;
}}

.lens .lensMoveHandle {{
  bottom: -16px !important;
}}

.globalHandleLabel {{
  position: absolute;
  bottom: -36px;
  font-family: Consolas, monospace;
  font-size: 11px;
  background: white;
  border: 1px solid #9bb4d6;
  color: #17344f;
  padding: 1px 4px;
  z-index: 1600;
  pointer-events: none;
  white-space: nowrap;
}}

.globalHandleLabel.left {{
  left: -18px;
}}

.globalHandleLabel.center {{
  left: 50%;
  transform: translateX(-50%);
}}

.globalHandleLabel.right {{
  right: -18px;
}}

#focusLabel {{
  font-size: 20px;
  font-weight: bold;
  color: #2f5f8f;
  margin-top: 22px;
  margin-bottom: 6px;
}}


#projectionLayer {{
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 2;
}}

.basinFrame {{
  border-left: 6px solid #8a5a2b !important;
  border-right: 6px solid #8a5a2b !important;
  border-top: 3px solid #8a5a2b !important;
  border-bottom: 3px solid #8a5a2b !important;
  background: rgba(138,90,43,0.12) !important;
  z-index: 55 !important;
}}

.inspectionFrame {{
  border-left: 4px solid #188a3a !important;
  border-right: 4px solid #188a3a !important;
  border-top: 2px solid #188a3a !important;
  border-bottom: 2px solid #188a3a !important;
  background: rgba(24,138,58,0.10) !important;
  z-index: 60 !important;
}}

.apertureFrame {{
  border-left: 2px solid #2f6f9f !important;
  border-right: 2px solid #2f6f9f !important;
  border-top: 1px solid #2f6f9f !important;
  border-bottom: 1px solid #2f6f9f !important;
  background: rgba(120,190,235,0.20) !important;
  z-index: 70 !important;
}}

.pointLabel {{
  display: none !important;
}}

#focusFrameLabelBand {{
  position: relative;
  height: 34px;
  margin-top: 4px;
  margin-bottom: 8px;
}}

.frameBottomLabel {{
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  font-family: Consolas, monospace;
  font-size: 11px;
  background: white;
  border: 1px solid #999;
  padding: 1px 4px;
  white-space: nowrap;
  z-index: 3;
}}

.frameBottomLabel.brown {{
  color: #6b421e;
  border-color: #8a5a2b;
}}

.frameBottomLabel.green {{
  color: #0f6f2c;
  border-color: #188a3a;
}}

.frameBottomLabel.blue {{
  color: #2f6f9f;
  border-color: #2f6f9f;
}}

#frameCountSummary {{
  text-align: center;
  font-family: Consolas, monospace;
  font-size: 13px;
  margin: 4px 0 10px 0;
}}

#frameCountSummary span {{
  margin: 0 10px;
}}

#frameCountSummary .brown {{
  color: #6b421e;
}}

#frameCountSummary .green {{
  color: #0f6f2c;
}}

#frameCountSummary .blue {{
  color: #2f6f9f;
}}

#focusLabel {{
  display: none !important;
}}

#focusBar {{
  margin-top: 34px;
}}

.csvTitle {{
  font-size: 16px !important;
  color: #002b63;
}}


.lens .lensMoveHandle {{
  width: 14px !important;
  height: 14px !important;
  border-radius: 50% !important;
  bottom: -25px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
}}

.lens .lensMoveHandle::before {{
  content: "";
  position: absolute;
  left: 50%;
  top: -16px;
  width: 2px;
  height: 16px;
  transform: translateX(-50%);
  background: #2f5f8f;
}}

.lens .lensResizeLeft,
.lens .lensResizeRight {{
  bottom: -18px !important;
}}

.globalHandleLabel.center {{
  bottom: -47px !important;
  font-size: 12px;
  font-weight: bold;
}}

.globalHandleLabel.left,
.globalHandleLabel.right {{
  bottom: -38px !important;
}}


/* V54C safe visual polish */

#globalBar {{
  height: 56px !important;
  margin-bottom: 46px !important;
}}

#focusBar {{
  height: 64px !important;
  margin-top: 34px !important;
}}

.legend,
#localContextLabel,
.localContextLabel {{
  display: none !important;
}}

/* softer blue global frame */
.lens {{
  border-left-color: #355f86 !important;
  border-right-color: #355f86 !important;
  background: rgba(80, 125, 165, 0.14) !important;
}}

.lens .lensHandle {{
  background: #355f86 !important;
  border-color: #24435f !important;
}}

/* global side handles: bracket-like */
.lens .lensResizeLeft,
.lens .lensResizeRight {{
  width: 8px !important;
  height: 46px !important;
  border-radius: 2px !important;
  background: rgba(53,95,134,0.20) !important;
  border: 2px solid #355f86 !important;
  bottom: -22px !important;
}}

.lens .lensResizeLeft {{
  left: -8px !important;
}}

.lens .lensResizeRight {{
  right: -8px !important;
}}

/* brown basin softer but visible */
.basinFrame {{
  border-left: 5px solid #b8875f !important;
  border-right: 5px solid #b8875f !important;
  border-top: 3px solid #b8875f !important;
  border-bottom: 3px solid #b8875f !important;
  background: rgba(184,135,95,0.13) !important;
}}

.basinFrame .lensHandle {{
  background: #b8875f !important;
  border-color: #7a5539 !important;
}}

/* green remains green, clearer side bounds */
.inspectionFrame {{
  border-left: 4px solid #2f8f55 !important;
  border-right: 4px solid #2f8f55 !important;
  border-top: 2px solid #2f8f55 !important;
  border-bottom: 2px solid #2f8f55 !important;
  background: rgba(47,143,85,0.10) !important;
}}

.inspectionFrame .lensHandle {{
  background: #2f8f55 !important;
  border-color: #1f663b !important;
}}

/* warm yellow aperture */
.apertureFrame {{
  border-left: 2px solid #d6ad2f !important;
  border-right: 2px solid #d6ad2f !important;
  border-top: 1px solid #d6ad2f !important;
  border-bottom: 1px solid #d6ad2f !important;
  background: rgba(244, 216, 112, 0.24) !important;
  box-shadow: inset 0 0 0 1px rgba(180,140,20,0.28) !important;
}}

#projectionLayer line {{
  stroke-width: 3.1 !important;
}}

.globalSpanLabel {{
  position:absolute;
  bottom:-66px;
  left:50%;
  transform:translateX(-50%);
  font-family:Consolas, monospace;
  font-size:14px;
  font-weight:bold;
  color:#24435f;
  background:white;
  padding:1px 6px;
  pointer-events:none;
  white-space:nowrap;
  z-index:1600;
}}


/* V54D local layout polish */

/* Make global and local bars thicker and less cramped */
#globalBar {{
  height: 72px !important;
  margin-bottom: 68px !important;
}}

#focusBar {{
  height: 78px !important;
  margin-top: 42px !important;
}}

/* Slightly separate global center/span labels */
.globalHandleLabel.center {{
  bottom: -42px !important;
  font-size: 13px !important;
  font-weight: bold !important;
}}

.globalSpanLabel {{
  bottom: -72px !important;
  font-size: 16px !important;
  font-weight: bold !important;
  border: 0 !important;
  background: transparent !important;
}}

/* Hide old top labels and status line robustly but safely */
.pointLabel {{
  display: none !important;
}}

.legend,
#localContextLabel,
.localContextLabel {{
  display: none !important;
}}

/* Local frame bottom label band */
#focusFrameLabelBand {{
  position: relative !important;
  height: 42px !important;
  margin-top: 8px !important;
  margin-bottom: 2px !important;
}}

.frameBottomLabel {{
  top: 6px !important;
  font-size: 11px !important;
  z-index: 20 !important;
}}

#frameCountSummary {{
  margin-top: 0 !important;
  margin-bottom: 12px !important;
  font-size: 14px !important;
}}

/* Warm focal aperture: override remaining inline red/orange */
.apertureFrame {{
  border-left: 2px solid #d9b43a !important;
  border-right: 2px solid #d9b43a !important;
  border-top: 1px solid #d9b43a !important;
  border-bottom: 1px solid #d9b43a !important;
  background: rgba(247, 222, 132, 0.26) !important;
  box-shadow: inset 0 0 0 1px rgba(175,135,20,0.25) !important;
}}

/* Buttons beside bars: smaller contained cluster */
#selectionPad {{
  max-width: 145px !important;
  margin-bottom: 8px !important;
}}

#selectionPad button {{
  font-size: 11px !important;
  padding: 3px 5px !important;
}}

/* CSV / notes / cards color families */
.csvControlGroup,
#csvPacketSurface {{
  border: 1px solid #d9a3ad !important;
  background: #fff3f5 !important;
}}

.csvTitle {{
  color: #8a3d4b !important;
  font-size: 17px !important;
}}

.stickyNoteBox {{
  background: #fff3a6 !important;
  border: 1px solid #d7b94d !important;
}}

#bookmarkCards {{
  border: 1px solid #a9c7e8 !important;
  background: #f5faff !important;
  padding: 8px !important;
  margin-top: 8px !important;
}}

#cardPackSurface {{
  border: 1px solid #d2a35c !important;
  background: #fff7ec !important;
}}

#linePreview {{
  border: 1px solid #a9c7e8 !important;
  background: #fbfdff !important;
}}

/* Projection lines stronger but still soft */
#projectionLayer line {{
  stroke-width: 3.2 !important;
}}


/* V54E size and spacing */

/* data bars taller; profile boxes less visually dominant */
#globalBar {{
  height: 88px !important;
}}

#focusBar {{
  height: 92px !important;
}}

.lensProfile,
.profileBox,
.globalProfile,
.focusProfile {{
  transform: scale(0.82);
  transform-origin: top left;
}}

/* keep lower evidence bars aligned with main lens bars */
#evidenceMicroBars,
#csvSelectionControls {{
  margin-left: 86px !important;
}}

.microBar {{
  height: 12px !important;
}}

/* Selection pad is its own small thing, left of the two bars */
#selectionPad {{
  max-width: 132px !important;
  margin-left: -86px !important;
  margin-bottom: 6px !important;
  border: 1px solid #bbb;
  background: #f8f8f8;
  padding: 6px;
}}

/* CSV is its own distinct contained block, not visually merged with selection pad */
.csvControlGroup {{
  margin-left: -86px !important;
  margin-top: 8px !important;
  border: 1px solid #d9a3ad !important;
  background: #fff3f5 !important;
  padding: 10px !important;
}}

/* sticky/cards/packs as related but distinct right-side surfaces */
.stickyNoteBox {{
  background: #fff3a6 !important;
  border: 1px solid #d7b94d !important;
  padding: 8px !important;
}}

#bookmarkCards {{
  border: 1px solid #e0b36b !important;
  background: #fff8ec !important;
  padding: 8px !important;
}}

#cardPackSurface {{
  border: 1px solid #d99a58 !important;
  background: #fff3e3 !important;
}}

/* Bottom labels: force below local map */
#focusFrameLabelBand {{
  margin-top: 14px !important;
  height: 46px !important;
}}

.frameBottomLabel {{
  top: 10px !important;
}}

/* Brown/green counts move left; focus count remains centered */
#frameCountSummary {{
  position: relative !important;
  height: 24px !important;
  margin-bottom: 12px !important;
}}

#frameCountSummary .brown {{
  position: absolute;
  left: 0;
}}

#frameCountSummary .green {{
  position: absolute;
  left: 92px;
}}

#frameCountSummary .blue {{
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-weight: bold;
}}


/* V54F2 local workbench refine */

.basinFrame .lensResizeLeft,
.basinFrame .lensResizeRight {{
  bottom: -24px !important;
  top: auto !important;
  height: 48px !important;
  width: 10px !important;
  background: rgba(184,135,95,0.22) !important;
  border: 2px solid #b8875f !important;
}}

.inspectionFrame .lensResizeLeft,
.inspectionFrame .lensResizeRight {{
  top: 34% !important;
  bottom: auto !important;
  height: 34% !important;
  width: 9px !important;
  background: rgba(47,143,85,0.24) !important;
  border: 2px solid #2f8f55 !important;
}}

.inspectionFrame .lensMoveHandle {{
  width: 14px !important;
  height: 14px !important;
  border-radius: 50% !important;
  bottom: -26px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
  background: #2f8f55 !important;
  border: 1px solid #1f663b !important;
}}

.inspectionFrame .lensMoveHandle::before {{
  content: "";
  position: absolute;
  left: 50%;
  top: -16px;
  width: 2px;
  height: 16px;
  transform: translateX(-50%);
  background: #2f8f55;
}}

.apertureFrame {{
  border-left: 2px solid #5f9fc8 !important;
  border-right: 2px solid #5f9fc8 !important;
  border-top: 1px solid #5f9fc8 !important;
  border-bottom: 1px solid #5f9fc8 !important;
  background: rgba(150, 205, 235, 0.24) !important;
  box-shadow: inset 0 0 0 1px rgba(75,130,165,0.25) !important;
}}

#frameCountSummary .brown {{
  display: none !important;
}}

#frameCountSummary .green {{
  left: 50% !important;
  transform: translateX(-50%) translateY(20px);
  font-weight: normal;
}}

#frameCountSummary .blue {{
  left: 50% !important;
  transform: translateX(-50%);
  font-weight: bold;
}}

#focusFrameLabelBand .brown {{
  display: none !important;
}}

#lowerLeftPanel {{
  position: relative;
}}

#selectionPad {{
  position: absolute !important;
  left: 6px !important;
  top: -84px !important;
  max-width: 120px !important;
  width: 112px !important;
  z-index: 50;
}}

#evidenceMicroBars {{
  margin-left: 130px !important;
}}

.csvControlGroup,
#csvPacketSurface {{
  border: 2px solid #d9a3ad !important;
  background: #fff3f5 !important;
}}

.csvTitle {{
  font-size: 19px !important;
  font-weight: bold !important;
}}

#noteCardRow {{
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 12px;
  align-items: start;
}}

.stickyNoteBox {{
  background: #fff3a6 !important;
  border: 1px solid #d7b94d !important;
}}

#bookmarkCards {{
  border: 2px solid #a9c7e8 !important;
  background: #f5faff !important;
  min-height: 120px;
}}

.bookmarkCard {{
  border: 2px solid #7faede !important;
  background: #ffffff !important;
  margin-bottom: 8px !important;
}}

#cardPackSurface {{
  border: 2px solid #d99a58 !important;
  background: #fff3e3 !important;
  margin-top: 12px !important;
}}


/* V54G final surface polish */

/* Make the actual data bars taller and profile widgets less dominant */
#globalBar {{
  height: 104px !important;
}}

#focusBar {{
  height: 104px !important;
}}

.lensProfile,
.profileBox,
.globalProfile,
.focusProfile {{
  transform: scale(0.72) !important;
  transform-origin: top left !important;
}}

/* Hide old above-frame labels and stray left labels */
.pointLabel,
#focusFrameLabelBand .brown,
#focusFrameLabelBand .green,
#focusFrameLabelBand .blue {{
  display: none !important;
}}

/* Keep only the clean count line below local: focus centered, green below */
#frameCountSummary .brown {{
  display: none !important;
}}

#frameCountSummary .blue {{
  left: 50% !important;
  transform: translateX(-50%) !important;
  font-weight: bold !important;
}}

#frameCountSummary .green {{
  left: 50% !important;
  transform: translateX(-50%) translateY(20px) !important;
  font-weight: normal !important;
}}

/* Final aperture override: light blue, no neon red/orange */
.apertureFrame {{
  border-left: 2px solid #5f9fc8 !important;
  border-right: 2px solid #5f9fc8 !important;
  border-top: 1px solid #5f9fc8 !important;
  border-bottom: 1px solid #5f9fc8 !important;
  background: rgba(150, 205, 235, 0.24) !important;
  box-shadow: inset 0 0 0 1px rgba(75,130,165,0.25) !important;
}}

/* Smaller, tighter selection pad in left gutter */
#selectionPad {{
  width: 78px !important;
  max-width: 78px !important;
  padding: 4px !important;
  gap: 3px !important;
  left: 18px !important;
  top: -74px !important;
  grid-template-columns: 36px 32px !important;
  grid-template-rows: 24px 24px 24px !important;
}}

#selectionPad button {{
  font-size: 9px !important;
  padding: 1px 2px !important;
  min-width: 0 !important;
}}

#selectAllFocus {{
  width: 36px !important;
}}

/* Align bars after smaller pad */
#evidenceMicroBars {{
  margin-left: 104px !important;
}}

/* CSV as one stronger contained section */
.csvControlGroup {{
  border: 2px solid #d9a3ad !important;
  background: #fff3f5 !important;
  padding: 10px !important;
  margin-bottom: 0 !important;
}}

#csvPacketSurface {{
  border: 2px solid #d9a3ad !important;
  border-top: 0 !important;
  background: #fff3f5 !important;
  padding: 10px !important;
  margin-top: 0 !important;
}}

.csvTitle {{
  font-size: 20px !important;
  font-weight: bold !important;
  color: #8a3d4b !important;
}}

/* Log area gets a clearer boundary */
#linePreview {{
  border: 2px solid #333 !important;
  background: #fbfdff !important;
}}

/* Sticky note and cards as related surface */
#noteCardRow {{
  grid-template-columns: 260px 1fr !important;
  gap: 12px !important;
}}

.stickyNoteBox {{
  background: #fff3a6 !important;
  border: 2px solid #d7b94d !important;
  padding: 8px !important;
}}

#bookmarkCards {{
  border: 2px solid #d7b94d !important;
  background: #fff7c7 !important;
  padding: 8px !important;
  min-height: 120px !important;
}}

.bookmarkCard {{
  position: relative !important;
  border: 2px solid #7faede !important;
  background: #ffffff !important;
  margin-bottom: 8px !important;
  padding: 8px 104px 8px 8px !important;
  min-height: 82px !important;
}}

/* Put card action buttons together in top-right: save, add, remove */
.bookmarkCard .saveBookmarkCsvButton,
.bookmarkCard .addBookmarkToPackButton,
.bookmarkCard .removeBookmarkButton {{
  position: absolute !important;
  right: 8px !important;
  width: 86px !important;
  font-size: 10px !important;
  margin: 0 !important;
}}

.bookmarkCard .saveBookmarkCsvButton {{
  top: 8px !important;
}}

.bookmarkCard .addBookmarkToPackButton {{
  top: 32px !important;
}}

.bookmarkCard .removeBookmarkButton {{
  top: 56px !important;
}}

/* Packs distinct orange surface below */
#cardPackSurface {{
  border: 2px solid #d99a58 !important;
  background: #fff3e3 !important;
  margin-top: 12px !important;
}}


/* V54G1 surface tighten */

/* local profile slightly lower */
#focusLensProfile {{
  margin-top: 12px !important;
}}

/* hide old local bound labels above frames */
.framePointLabel {{
  display: none !important;
}}

#linePreviewLabel {{
  display: none !important;
}}

/* force aperture away from old neon red/orange */
.focusRangeFrame.apertureFrame {{
  border-left: 2px solid #5f9fc8 !important;
  border-right: 2px solid #5f9fc8 !important;
  border-top: 1px solid #5f9fc8 !important;
  border-bottom: 1px solid #5f9fc8 !important;
  background: rgba(150, 205, 235, 0.24) !important;
  box-shadow: inset 0 0 0 1px rgba(75,130,165,0.25) !important;
}}

/* switch cluster a little right, CSV a little down */
#selectionPad {{
  left: 30px !important;
}}

.csvControlGroup {{
  margin-top: 18px !important;
}}

/* sticky note surface */
#noteCardRow > .box:first-child {{
  background: #fff3a6 !important;
  border: 2px solid #d7b94d !important;
  padding: 10px !important;
}}

#noteCardRow > .box:first-child > div:first-child {{
  font-size: 20px !important;
  font-weight: bold !important;
  margin-bottom: 8px !important;
}}

/* card pack heading */
#cardPackSurface b:first-child {{
  font-size: 18px !important;
}}

/* card buttons right-side stack */
.bookmarkCard {{
  position: relative !important;
  padding-right: 112px !important;
}}

.bookmarkCard .saveBookmarkCsvButton,
.bookmarkCard .addBookmarkToPackButton,
.bookmarkCard .removeBookmarkButton {{
  position: absolute !important;
  right: 8px !important;
  width: 94px !important;
  font-size: 10px !important;
  margin: 0 !important;
}}

.bookmarkCard .saveBookmarkCsvButton {{
  top: 8px !important;
}}

.bookmarkCard .addBookmarkToPackButton {{
  top: 32px !important;
}}

.bookmarkCard .removeBookmarkButton {{
  top: 56px !important;
}}


/* V54G2 color scheme shift */

/* local profile slightly lower */
#focusLensProfile {{
  margin-top: 18px !important;
}}

/* brown boundary thicker */
.basinFrame {{
  border-left: 6px solid #b8875f !important;
  border-right: 6px solid #b8875f !important;
  border-top: 3px solid #b8875f !important;
  border-bottom: 3px solid #b8875f !important;
  background: rgba(184,135,95,0.12) !important;
}}

/* green inspection becomes blue context frame */
.inspectionFrame {{
  border-left: 5px solid #4f8fbd !important;
  border-right: 5px solid #4f8fbd !important;
  border-top: 2px solid #4f8fbd !important;
  border-bottom: 2px solid #4f8fbd !important;
  background: rgba(140,195,230,0.18) !important;
}}

.inspectionFrame .lensHandle {{
  background: #4f8fbd !important;
  border-color: #2f6388 !important;
}}

.inspectionFrame .lensMoveHandle {{
  background: #4f8fbd !important;
  border-color: #2f6388 !important;
}}

.inspectionFrame .lensMoveHandle::before {{
  background: #4f8fbd !important;
}}

/* focus aperture becomes warm yellow */
.focusRangeFrame.apertureFrame,
.apertureFrame {{
  border-left: 2px solid #d9b43a !important;
  border-right: 2px solid #d9b43a !important;
  border-top: 1px solid #d9b43a !important;
  border-bottom: 1px solid #d9b43a !important;
  background: rgba(247,222,132,0.30) !important;
  box-shadow: inset 0 0 0 1px rgba(175,135,20,0.25) !important;
}}

/* local labels below, color shifted */
.frameBottomLabel.brown {{
  color: #7a5539 !important;
  border-color: #b8875f !important;
}}

.frameBottomLabel.green {{
  color: #2f6388 !important;
  border-color: #4f8fbd !important;
}}

.frameBottomLabel.blue {{
  color: #9a771e !important;
  border-color: #d9b43a !important;
}}

#frameCountSummary .green {{
  color: #2f6388 !important;
}}

#frameCountSummary .blue {{
  color: #9a771e !important;
}}

/* nudge selection buttons and CSV */
#selectionPad {{
  left: 36px !important;
}}

.csvControlGroup {{
  margin-top: 22px !important;
}}

/* CSV button color shifts */
.csvGreenButton {{
  border: 2px solid #4f8fbd !important;
  background: #eaf5fd !important;
}}

.csvFocusButton {{
  border: 2px solid #d9b43a !important;
  background: #fff6cf !important;
}}


/* V54G3B safe settle */

/* brown: thicker, but do NOT raise above blue handles */
.basinFrame {{
  border-left: 7px solid #9b6438 !important;
  border-right: 7px solid #9b6438 !important;
  border-top: 4px solid #9b6438 !important;
  border-bottom: 4px solid #9b6438 !important;
  background: rgba(155,100,56,0.13) !important;
  box-shadow: 0 0 0 1px rgba(95,55,28,0.35) !important;
  z-index: 50 !important;
  pointer-events: none !important;
}}

.basinFrame .lensHandle {{
  pointer-events: auto !important;
  background: #9b6438 !important;
  border-color: #623719 !important;
}}

/* blue local frame: keep drag handles working */
.inspectionFrame {{
  border-left: 6px solid #4f8fbd !important;
  border-right: 6px solid #4f8fbd !important;
  border-top: 2px solid #4f8fbd !important;
  border-bottom: 2px solid #4f8fbd !important;
  background: rgba(140,195,230,0.18) !important;
  z-index: 70 !important;
  pointer-events: auto !important;
}}

.inspectionFrame .lensHandle {{
  pointer-events: auto !important;
  background: #4f8fbd !important;
  border-color: #2f6388 !important;
}}

/* yellow focus */
.focusRangeFrame.apertureFrame,
.apertureFrame {{
  border-left: 2px solid #d9b43a !important;
  border-right: 2px solid #d9b43a !important;
  border-top: 1px solid #d9b43a !important;
  border-bottom: 1px solid #d9b43a !important;
  background: rgba(247,222,132,0.30) !important;
  box-shadow: inset 0 0 0 1px rgba(175,135,20,0.25) !important;
  pointer-events: none !important;
}}

/* lower local profile */
#focusLensProfile,
[id*="focus"][id*="Profile"],
.focusProfile {{
  margin-top: 24px !important;
}}

/* selection and CSV nudges */
#selectionPad {{
  left: 44px !important;
}}

.csvControlGroup {{
  margin-top: 30px !important;
}}

#lowerRightPanel {{
  padding-top: 14px !important;
}}

/* sticky note input containment */
.stickyNoteBox input,
#noteText,
#unresolvedText {{
  width: calc(100% - 12px) !important;
  box-sizing: border-box !important;
}}

/* suppress old fixed/above labels */
.pointLabel,
.framePointLabel {{
  display: none !important;
}}

/* custom local label band */
#focusFrameLabelBand {{
  height: 44px !important;
  margin-top: 8px !important;
}}

.frameBottomLabel {{
  top: 8px !important;
  z-index: 200 !important;
}}

.frameBottomLabel.brown {{
  display: block !important;
  color: #623719 !important;
  border-color: #9b6438 !important;
}}

.frameBottomLabel.green {{
  display: block !important;
  color: #2f6388 !important;
  border-color: #4f8fbd !important;
}}

.frameBottomLabel.blue {{
  display: block !important;
  color: #9a771e !important;
  border-color: #d9b43a !important;
}}

#frameCountSummary {{
  position: relative !important;
  height: 42px !important;
  margin-top: 0 !important;
}}

#frameCountSummary .brown {{
  display: none !important;
}}

#frameCountSummary .blue {{
  position: absolute !important;
  top: 0 !important;
  font-weight: bold !important;
  color: #9a771e !important;
}}

#frameCountSummary .green {{
  position: absolute !important;
  top: 20px !important;
  font-weight: normal !important;
  color: #2f6388 !important;
}}


/* V54G3C final alignment */

/* move the focus/blue count pair slightly lower under the moving tab */
#frameCountSummary {{
  margin-top: 10px !important;
}}

#frameCountSummary .blue {{
  top: 8px !important;
}}

#frameCountSummary .green {{
  top: 28px !important;
}}

/* lower the local profile a small amount */
#focusLensProfile,
[id*="focus"][id*="Profile"],
.focusProfile {{
  margin-top: 30px !important;
}}

/* nudge selection pad slightly right; keep its left near profile column */
#selectionPad {{
  left: 52px !important;
}}

</style>
</head>
<body>
<div id="wrap">
<h1>Global Focus Lens</h1>

<div class="box lensSizeBox">
  <div>Global window</div>
  <input id="globalSizeDial" type="range" min="0" max="{len(sizes)-1}" value="{max(0, sizes.index(350) if 350 in sizes else 0)}" step="1">
  <div id="globalSizeLabel" class="label"></div>
</div>

<div class="label" id="globalLabel"></div>
<div id="globalBar" class="bar"></div>

<div class="controls">
  <div class="box">
    <div>Focus width</div>
    <input id="spanDial" type="range" min="500" max="120000" value="3400" step="100">
    <div id="spanLabel" class="label"></div>
  </div>

  <div class="box" style="grid-column: span 2;">
    <div>Focus center</div>
    <input id="centerDial" type="range" min="1" max="{max_line}" value="31300" step="50">
    <div id="centerLabel" class="label"></div>
  </div>
</div>

<div class="box lensSizeBox">
  <div>Focus window</div>
  <input id="focusSizeDial" type="range" min="0" max="{len(sizes)-1}" value="{max(0, sizes.index(100) if 100 in sizes else 0)}" step="1">
  <div id="focusSizeLabel" class="label"></div>
</div>

<div class="label" id="focusLabel"></div>
<div id="focusBar" class="bar focusBar"></div>



<div class="label" id="linePreviewLabel">Selected raw lines</div>

<div id="evidenceMicroBars" style="margin-top:22px; margin-bottom:14px;">
  <div id="postureMicroBar" class="microBar"></div>
  <div id="preservationMicroBar" class="microBar"></div>
</div>

<div id="csvSelectionControls" style="margin:10px 0 12px 0; padding:8px; border:1px solid #bbb; background:#fafafa;">
  <div style="margin-bottom:6px;">
    <button id="selectAllFocus" style="font-size:14px;">Toggle all focus</button>
    <button id="deselectAllFocus" style="font-size:14px; display:none;">Deselect all focus</button>
    <button id="selectWhiteFocus" style="font-size:14px;">Toggle white</button>
    <button id="selectGreyFocus" style="font-size:14px;">Toggle grey</button>
    <button id="selectBlackFocus" style="font-size:14px;">Toggle black</button>
  </div>
  <div>
    <button id="saveBrownCsv" style="font-size:14px;">Save brown to CSV</button>
    <button id="saveGreenCsv" style="font-size:14px;">Save green to CSV</button>
    <button id="saveApertureCsv" style="font-size:14px;">Save focus center to CSV</button>
    <button id="downloadCsv" style="font-size:14px;">Download CSV</button>
  </div>
  <div id="csvStatus" style="margin-top:8px; font-family:Consolas, monospace; font-size:12px;"></div>
</div>


<div id="csvPacketSurface"
     style="margin-top:10px;
            border:1px solid #999;
            padding:8px;
            background:#fafafa;
            font-family:Consolas, monospace;
            font-size:12px;">
  <b>CSV packets</b>
  <div id="csvPacketList" style="margin-top:8px;"></div>

  <div style="margin-top:8px;">
    <button id="clearCsvPackets" style="font-size:14px;">
      Clear CSV packets
    </button>
  </div>
</div>


<pre id="linePreview">Click or drag inside the focus lens to preview precise raw source lines.</pre>

<div class="box">
  <div>sticky note</div>
  <input id="noteText" type="text" placeholder="comment 1" style="width:100%; font-size:16px; padding:6px;">
  <input id="unresolvedText" type="text" placeholder="comment 2" style="width:100%; font-size:16px; padding:6px; margin-top:8px;">
  <button id="saveBookmark" style="margin-top:10px; font-size:16px;">Save sticky note</button>
  <pre id="bookmarkPreview" style="border:1px solid #999; padding:10px; white-space:pre-wrap; font-family:Consolas, monospace; font-size:13px;"></pre>

<div id="bookmarkCards"></div>

<div id="cardPackSurface"
     style="margin-top:12px;
            border:1px solid #999;
            padding:8px;
            background:#fafafa;
            font-family:Consolas, monospace;
            font-size:12px;">
  <b>Card packs</b>

  <div style="margin-top:8px;">
    <input id="newPackName"
           type="text"
           placeholder="pack name"
           style="font-size:14px; padding:4px; width:220px;">
    <button id="createCardPack" style="font-size:14px;">Create pack</button>
  </div>

  <div id="cardPackList" style="margin-top:8px;"></div>
</div>

</div>

<div class="note">
Use the upper bar as the map. Click or drag on it to choose a region. Mouse wheel over the global map changes the focus window size. Click or drag inside the focus lens to preview raw lines.
</div>
</div>

<script>
/* SECTION 1 — DOM REFERENCES */
const data = __PAYLOAD__;

const globalSizeDial = document.getElementById("globalSizeDial");
const focusSizeDial = document.getElementById("focusSizeDial");
const spanDial = document.getElementById("spanDial");
const centerDial = document.getElementById("centerDial");
const globalBar = document.getElementById("globalBar");
const focusBar = document.getElementById("focusBar");
const globalSizeLabel = document.getElementById("globalSizeLabel");
const focusSizeLabel = document.getElementById("focusSizeLabel");
const spanLabel = document.getElementById("spanLabel");
const centerLabel = document.getElementById("centerLabel");
const globalLabel = document.getElementById("globalLabel");
const focusLabel = document.getElementById("focusLabel");
const linePreview = document.getElementById("linePreview");
const linePreviewLabel = document.getElementById("linePreviewLabel");
const postureMicroBar = document.getElementById("postureMicroBar");
const preservationMicroBar = document.getElementById("preservationMicroBar");
const noteText = document.getElementById("noteText");
const unresolvedText = document.getElementById("unresolvedText");
const saveBookmark = document.getElementById("saveBookmark");
const selectAllFocus = document.getElementById("selectAllFocus");
const deselectAllFocus = document.getElementById("deselectAllFocus");
const selectWhiteFocus = document.getElementById("selectWhiteFocus");
const selectGreyFocus = document.getElementById("selectGreyFocus");
const selectBlackFocus = document.getElementById("selectBlackFocus");
const saveBrownCsv = document.getElementById("saveBrownCsv");
const saveGreenCsv = document.getElementById("saveGreenCsv");
const saveApertureCsv = document.getElementById("saveApertureCsv");
const downloadCsv = document.getElementById("downloadCsv");
const csvStatus = document.getElementById("csvStatus");
const csvPacketList = document.getElementById("csvPacketList");
const clearCsvPackets = document.getElementById("clearCsvPackets");
const bookmarkPreview = document.getElementById("bookmarkPreview");
const bookmarkCards = document.getElementById("bookmarkCards");
const cardPackList = document.getElementById("cardPackList");
const newPackName = document.getElementById("newPackName");
const createCardPack = document.getElementById("createCardPack");

let bookmarks = [];
let csvPackets = [];
let cardPacks = [];
let activePackIndex = null;


/* SECTION 2 — STATE */
let dragging = false;
let dragStartLine = null;
let dragBox = null;

let focusDragging = false;
let focusDragStartLine = null;
let focusDragBox = null;

let basinStart = null;
let basinEnd = null;
let inspectionStart = null;
let inspectionEnd = null;

let apertureStart = null;
let apertureEnd = null;
const apertureLimit = 250;
const inspectionLimit = 5000;

let selectionMask = {{}};
let preservationPaintActive = false;
let preservationPaintValue = true;

function lineFromMicroBarMouse(evt) {{
  if (apertureStart === null || apertureEnd === null) return null;

  const bar = evt.currentTarget;
  const rect = bar.getBoundingClientRect();
  const x = clamp(evt.clientX - rect.left, 0, rect.width - 1);

  const count = apertureEnd - apertureStart + 1;
  const idx = clamp(Math.floor((x / rect.width) * count), 0, count - 1);

  return apertureStart + idx;
}}

function repaintLineFromMicroBar(evt) {{
  const line = lineFromMicroBarMouse(evt);
  if (line === null) return;

  setLineIncluded(line, preservationPaintValue);
  renderEvidenceMicroBars(state());
  renderRawRowsForCurrentState();
}}

function wireMicroBarPaint() {{
  [postureMicroBar, preservationMicroBar].forEach(bar => {{
    bar.addEventListener("mousedown", evt => {{
      const line = lineFromMicroBarMouse(evt);
      if (line === null) return;

      preservationPaintValue = !isLineIncluded(line);
      preservationPaintActive = true;

      setLineIncluded(line, preservationPaintValue);
      renderEvidenceMicroBars(state());
      renderRawRowsForCurrentState();
    }});

    bar.addEventListener("mousemove", evt => {{
      if (!preservationPaintActive) return;
      repaintLineFromMicroBar(evt);
    }});
  }});

  const stopPaint = () => {{
    preservationPaintActive = false;
  }};

  document.addEventListener("mouseup", stopPaint);

  const evidenceBars = document.getElementById("evidenceMicroBars");
  if (evidenceBars) {{
    evidenceBars.addEventListener("mouseleave", stopPaint);
  }}
}}

function clamp(v, lo, hi) {{ return Math.max(lo, Math.min(hi, v)); }}

function resetSelectionMaskForInspection() {{
  selectionMask = {{}};

  if (inspectionStart === null || inspectionEnd === null) return;

  for (let i = inspectionStart; i <= inspectionEnd; i++) {{
    selectionMask[String(i)] = true;
  }}
}}

function setLineIncluded(line, value) {{
  selectionMask[String(line)] = value ? true : false;
}}

function isLineIncluded(line) {{
  const key = String(line);
  if (!(key in selectionMask)) {{
    selectionMask[key] = true;
  }}
  return selectionMask[key] === true;
}}

function toggleLineIncluded(line) {{
  setLineIncluded(line, !isLineIncluded(line));
}}

function selectedLinesInInspection() {{
  let out = [];

  if (inspectionStart === null || inspectionEnd === null) return out;

  for (let i = inspectionStart; i <= inspectionEnd; i++) {{
    if (isLineIncluded(i)) out.push(i);
  }}

  return out;
}}

function deriveGlobalState() {{
  return {{
    globalSize: data.sizes[parseInt(globalSizeDial.value)]
  }};
}}

function deriveFocusConstitutionState() {{
  return {{
    focusSize: data.sizes[parseInt(focusSizeDial.value)]
  }};
}}

function deriveLensGeometry() {{
  const span = parseInt(spanDial.value);
  let center = parseInt(centerDial.value);

  let start = Math.round(center - span / 2);
  let end = Math.round(center + span / 2);

  if (start < 1) {{
    start = 1;
    end = span;
  }}

  if (end > data.max_line) {{
    end = data.max_line;
    start = data.max_line - span + 1;
  }}

  start = clamp(start, 1, data.max_line);
  end = clamp(end, 1, data.max_line);

  center = Math.round((start + end) / 2);

  return {{span, center, start, end}};
}}

function state() {{
  const globalState = deriveGlobalState();
  const focusState = deriveFocusConstitutionState();
  const lensGeometry = deriveLensGeometry();

  centerDial.value = lensGeometry.center;

  return {{
    ...globalState,
    ...focusState,
    ...lensGeometry
  }};
}}

function lineFromMouse(evt, bar, start, end) {{
  const rect = bar.getBoundingClientRect();
  const x = clamp(evt.clientX - rect.left, 0, rect.width);
  return Math.round(start + (x / rect.width) * (end - start));
}}

function clearBar(bar) {{ bar.innerHTML = ""; }}

function addSeg(bar, cls, widthPct) {{
  const div = document.createElement("div");
  div.className = "seg " + cls;
  div.style.width = widthPct + "%";
  bar.appendChild(div);
}}

/* SECTION 4 — BAR RENDERING */
function renderBar(bar, size, start, end, fullScale) {{
  clearBar(bar);

  const rows = data.rows.filter(r =>
    parseInt(r.window_size) === size &&
    r.line_end >= start &&
    r.line_start <= end
  );

  const span = end - start + 1;

  rows.forEach(r => {{
    const localStart = Math.max(r.line_start, start);
    const localEnd = Math.min(r.line_end, end);
    const total = localEnd - localStart + 1;

    [["stable", r.stable_share], ["middle", r.middle_share], ["residual", r.residual_share]].forEach(pair => {{
      const denom = fullScale ? data.max_line : span;
      addSeg(bar, pair[0], pair[1] * total / denom * 100);
    }});
  }});
}}

/* SECTION 5 — GLOBAL LENS */
function addHandle(parent, cls, kind, mode) {{
  const h = document.createElement("div");
  h.className = "lensHandle " + cls;

  h.addEventListener("mousedown", evt => {{
    evt.preventDefault();
    evt.stopPropagation();
    beginLensHandleDrag(kind, mode, evt);
  }});

  parent.appendChild(h);
}}


function ensureProjectionLayer() {{
  let svg = document.getElementById("projectionLayer");
  if (svg) return svg;

  svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.id = "projectionLayer";
  document.body.appendChild(svg);
  return svg;
}}

function addProjectionLine(svg, x1, y1, x2, y2) {{
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1);
  line.setAttribute("y1", y1);
  line.setAttribute("x2", x2);
  line.setAttribute("y2", y2);
  line.setAttribute("stroke", "#2f5f8f");
  line.setAttribute("stroke-width", "1.2");
  line.setAttribute("opacity", "0.55");
  svg.appendChild(line);
}}

function renderProjectionLines() {{
  const svg = ensureProjectionLayer();
  svg.innerHTML = "";

  const globalLens = globalBar.querySelector(".lens");
  if (!globalLens) return;

  const g = globalLens.getBoundingClientRect();
  const f = focusBar.getBoundingClientRect();

  addProjectionLine(svg, g.left, g.bottom, f.left, f.top);
  addProjectionLine(svg, g.right, g.bottom, f.right, f.top);
}}

function addGlobalHandleLabels(parent, start, end) {{
  const center = Math.round((start + end) / 2);

  const left = document.createElement("div");
  left.className = "globalHandleLabel left";
  left.textContent = start;

  const mid = document.createElement("div");
  mid.className = "globalHandleLabel center";
  mid.textContent = center;

  const right = document.createElement("div");
  right.className = "globalHandleLabel right";
  right.textContent = end;

  const span = document.createElement("div");
  span.className = "globalSpanLabel";
  span.textContent = end - start + 1;

  parent.appendChild(left);
  parent.appendChild(mid);
  parent.appendChild(right);
  parent.appendChild(span);
}}

function addLens(start, end) {{
  const lens = document.createElement("div");
  lens.className = "lens";
  lens.style.left = ((start - 1) / data.max_line * 100) + "%";
  lens.style.width = ((end - start + 1) / data.max_line * 100) + "%";

  addHandle(lens, "lensMoveHandle", "global", "move");
  addHandle(lens, "lensResizeLeft", "global", "left");
  addHandle(lens, "lensResizeRight", "global", "right");
  addGlobalHandleLabels(lens, start, end);

  globalBar.appendChild(lens);
}}

/* SECTION 6 — RAW EVIDENCE PREVIEW */

function setBasin(a, b) {{
  const s = state();

  basinStart = clamp(Math.min(a, b), s.start, s.end);
  basinEnd = clamp(Math.max(a, b), s.start, s.end);
}}

function clearBasin() {{
  basinStart = null;
  basinEnd = null;
  inspectionStart = null;
  inspectionEnd = null;
}}

function basinContains(a, b) {{
  if (basinStart === null || basinEnd === null) return false;
  return a >= basinStart && b <= basinEnd;
}}

function deriveInspectionWindow(a, b) {{
  const width = b - a + 1;

  if (width <= inspectionLimit) {{
    return {{ start: a, end: b }};
  }}

  const mid = Math.round((a + b) / 2);
  let start = Math.round(mid - inspectionLimit / 2);
  let end = start + inspectionLimit - 1;

  if (start < a) {{
    start = a;
    end = start + inspectionLimit - 1;
  }}

  if (end > b) {{
    end = b;
    start = end - inspectionLimit + 1;
  }}

  return {{ start: start, end: end }};
}}

function setInspectionFromBasin() {{
  if (basinStart === null || basinEnd === null) return;

  const shown = deriveInspectionWindow(basinStart, basinEnd);
  inspectionStart = shown.start;
  inspectionEnd = shown.end;
  resetSelectionMaskForInspection();
}}

function addPointLabels(frame, a, b) {{
  const mid = Math.round((a + b) / 2);

  const left = document.createElement("div");
  left.className = "framePointLabel left";
  left.textContent = a;

  const center = document.createElement("div");
  center.className = "framePointLabel mid";
  center.textContent = mid;

  const right = document.createElement("div");
  right.className = "framePointLabel right";
  right.textContent = b;

  frame.appendChild(left);
  frame.appendChild(center);
  frame.appendChild(right);
}}

function addFocusFrame(cls, a, b, s) {{
  if (a === null || b === null) return;

  const span = Math.max(1, s.end - s.start + 1);
  a = clamp(a, s.start, s.end);
  b = clamp(b, s.start, s.end);

  const leftPct = ((a - s.start) / span) * 100;
  const widthPct = ((b - a + 1) / span) * 100;

  let insetPx = 0;
  if (cls === "inspectionFrame") insetPx = 3;
  if (cls === "apertureFrame") insetPx = 7;

  const frame = document.createElement("div");
  frame.className = "focusRangeFrame " + cls;
  frame.style.left = "calc(" + leftPct + "% + " + insetPx + "px)";
  frame.style.width = "calc(" + widthPct + "% - " + (insetPx * 2) + "px)";

  addPointLabels(frame, a, b);

  if (cls === "basinFrame") {{
    addHandle(frame, "lensResizeLeft", "basin", "left");
    addHandle(frame, "lensResizeRight", "basin", "right");
  }}

  if (cls === "inspectionFrame") {{
    addHandle(frame, "lensMoveHandle", "inspection", "move");
    addHandle(frame, "lensResizeLeft", "inspection", "left");
    addHandle(frame, "lensResizeRight", "inspection", "right");
  }}

  focusBar.appendChild(frame);
}}

function renderFocusFrames(s) {{
  if (inspectionStart !== null && inspectionEnd !== null) {{
    deriveApertureFromInspection();
  }}

  if (basinStart !== null && basinEnd !== null) {{
    addFocusFrame("basinFrame", basinStart, basinEnd, s);
  }}

  if (inspectionStart !== null && inspectionEnd !== null) {{
    addFocusFrame("inspectionFrame", inspectionStart, inspectionEnd, s);
  }}

  if (apertureStart !== null && apertureEnd !== null) {{
    addFocusFrame("apertureFrame", apertureStart, apertureEnd, s);
  }}
}}


function previewLineRange(startLine, endLine) {{
  const s = state();

  const rawStart = Math.min(startLine, endLine);
  const rawEnd = Math.max(startLine, endLine);

  setBasin(rawStart, rawEnd);
  setInspectionFromBasin();
renderInspectionPreviewOnly();
render();
return;

  const start = inspectionStart;
  const end = inspectionEnd;

  let out = [];
  for (let i = start; i <= end; i++) {{
    const line = data.source_lines[i - 1] || "";
    out.push(String(i).padStart(8, " ") + " | " + line);
  }}

  let suffix = "";
  if (basinStart !== inspectionStart || basinEnd !== inspectionEnd) {{
    suffix =
      "\\n\\n... inspection capped at " + inspectionLimit +
      " lines. Saving basin continues: " + basinStart + "-" + basinEnd + ".";
  }}

  linePreviewLabel.innerHTML =
    "selected for inspection: " + inspectionStart + "-" + inspectionEnd +
    " | selected for saving: " + basinStart + "-" + basinEnd;

  linePreview.textContent = out.join("\\n") + suffix;

  render();
}}



function deriveApertureFromInspection() {{
  if (inspectionStart === null || inspectionEnd === null) return;

  const width = inspectionEnd - inspectionStart + 1;

  if (width <= apertureLimit) {{
    apertureStart = inspectionStart;
    apertureEnd = inspectionEnd;
    return;
  }}

  const mid = Math.round((inspectionStart + inspectionEnd) / 2);

  let a = Math.round(mid - apertureLimit / 2);
  let b = a + apertureLimit - 1;

  if (a < inspectionStart) {{
    a = inspectionStart;
    b = a + apertureLimit - 1;
  }}

  if (b > inspectionEnd) {{
    b = inspectionEnd;
    a = b - apertureLimit + 1;
  }}

  apertureStart = a;
  apertureEnd = b;
}}

function renderInspectionPreviewOnly() {{
  if (inspectionStart === null || inspectionEnd === null) return;

  deriveApertureFromInspection();
  renderRawRowsForCurrentState();

  linePreviewLabel.innerHTML =
    "green inspection: " + inspectionStart + "-" + inspectionEnd +
    " | focal aperture: " + apertureStart + "-" + apertureEnd +
    " | brown saving: " + basinStart + "-" + basinEnd;
}}


function escapeHtml(s) {{
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}}

function renderRawRowsForCurrentState() {{
  if (apertureStart === null || apertureEnd === null) return;

  let html = [];

  for (let i = apertureStart; i <= apertureEnd; i++) {{
    const line = data.source_lines[i - 1] || "";
    const included = isLineIncluded(i);
    const checked = included ? "checked" : "";
    const rowClass = included ? "rawLogRow" : "rawLogRow excluded";

    html.push(
      '<div class="' + rowClass + '" data-line="' + i + '">' +
      '<input type="checkbox" class="rawIncludeBox" data-line="' + i + '" ' + checked + '> ' +
      '<span class="rawLineNumber">' + String(i).padStart(8, " ") + '</span>' +
      ' | ' +
      '<span class="rawLineText">' + escapeHtml(line) + '</span>' +
      '</div>'
    );
  }}

  let suffix = "";

  if (apertureStart !== inspectionStart || apertureEnd !== inspectionEnd) {{
    suffix +=
      '<div class="rawSuffix">... focal aperture shows ' + apertureStart + '-' + apertureEnd +
      ' inside green inspection span ' + inspectionStart + '-' + inspectionEnd + '.</div>';
  }}

  if (basinStart !== inspectionStart || basinEnd !== inspectionEnd) {{
    suffix +=
      '<div class="rawSuffix">Saving basin continues: ' + basinStart + '-' + basinEnd + '.</div>';
  }}

  linePreview.innerHTML = html.join("") + suffix;

  document.querySelectorAll(".rawIncludeBox").forEach(cb => {{
    cb.addEventListener("change", evt => {{
      const line = parseInt(evt.target.getAttribute("data-line"));
      setLineIncluded(line, evt.target.checked);
      renderEvidenceMicroBars(state());
      renderRawRowsForCurrentState();
    }});
  }});
}}

function setInspectionRange(a, b) {{
  let lo = Math.min(a, b);
  let hi = Math.max(a, b);

  if (basinStart !== null && basinEnd !== null) {{
    lo = clamp(lo, basinStart, basinEnd);
    hi = clamp(hi, basinStart, basinEnd);
  }}

  inspectionStart = lo;
  inspectionEnd = hi;
  for (let i = inspectionStart; i <= inspectionEnd; i++) {{
  isLineIncluded(i);
}}
}}



function previewInspectionRange(startLine, endLine) {{
  setInspectionRange(startLine, endLine);
  renderInspectionPreviewOnly();
  render();
}}

function previewLines(centerLine) {{
  const radius = 8;
  const a = centerLine - radius;
  const b = centerLine + radius;

  if (basinContains(a, b)) {{
    previewInspectionRange(a, b);
  }} else {{
    previewLineRange(a, b);
  }}
}}

/* SECTION 7 — MAIN RENDER */
function renderControls(s) {{
  globalSizeLabel.innerHTML = s.globalSize;
  focusSizeLabel.innerHTML = s.focusSize;
  spanLabel.innerHTML = "focus width: " + s.span + " lines";
  centerLabel.innerHTML = "focus center: " + s.center;
}}

function renderBars(s) {{
  renderBar(globalBar, s.globalSize, 1, data.max_line, true);
  renderBar(focusBar, s.focusSize, s.start, s.end, false);
}}


function renderLenses(s) {{
  addLens(s.start, s.end);
  renderFocusFrames(s);
}}

function renderLabels(s) {{
  globalLabel.innerHTML = "Global map<br>lines 1-" + data.max_line;
  globalLabel.style.textAlign = "left";
  globalLabel.style.marginLeft = "0";
  focusLabel.innerHTML = String(s.end - s.start + 1);
}}

function dominantPartForLine(line, s) {{
  const rows = data.rows.filter(r =>
    parseInt(r.window_size) === s.focusSize &&
    r.line_start <= line &&
    r.line_end >= line
  );

  if (rows.length === 0) return "stable";

  const r = rows[0];

  if (r.residual_share >= r.stable_share && r.residual_share >= r.middle_share) return "residual";
  if (r.middle_share >= r.stable_share && r.middle_share >= r.residual_share) return "middle";
  return "stable";
}}

function renderEvidenceMicroBars(s) {{
  postureMicroBar.innerHTML = "";
  preservationMicroBar.innerHTML = "";

  if (apertureStart === null || apertureEnd === null) {{
    return;
  }}

  for (let i = apertureStart; i <= apertureEnd; i++) {{
    const part = dominantPartForLine(i, s);

    const posture = document.createElement("div");
    posture.className =
      "microBlock " +
      (part === "residual" ? "microResidual" : part === "middle" ? "microMiddle" : "microStable");
    posture.title = i + " | " + part;
    postureMicroBar.appendChild(posture);

    const preserved = document.createElement("div");
    preserved.className =
      "microBlock " +
      (isLineIncluded(i) ? "microIncluded" : "microExcluded");
    preserved.title = i + " | " + (isLineIncluded(i) ? "included" : "excluded");
    preservationMicroBar.appendChild(preserved);
  }}
}}

function render() {{
  const s = state();

  renderControls(s);
  renderBars(s);
  renderLenses(s);
  renderLabels(s);
  renderEvidenceMicroBars(s);
  ensureLensProfiles();
  updateLensProfiles();
  setTimeout(() => {{
    renderFocusBottomLabelsAndCounts();
    renderProjectionLines();
    hideOldContextStatusLineSafe();
    forceV54DVisuals();
    forceV54ELayout();
    forceV54F2Visuals();
    refineNoteCardLayout();
  }}, 0);
}}

let activeLensHandleDrag = null;

function beginLensHandleDrag(kind, mode, evt) {{
  const s = state();

  if (kind === "inspection" && (inspectionStart === null || inspectionEnd === null)) return;
  if (kind === "basin" && (basinStart === null || basinEnd === null)) return;

  activeLensHandleDrag = {{
    kind: kind,
    mode: mode,
    mouseStart: evt.clientX,
    start: kind === "global" ? s.start : (kind === "basin" ? basinStart : inspectionStart),
    end: kind === "global" ? s.end : (kind === "basin" ? basinEnd : inspectionEnd)
  }};
}}

function moveRangeByDelta(start, end, delta, lo, hi) {{
  const width = end - start + 1;
  let a = start + delta;
  let b = end + delta;

  if (a < lo) {{
    a = lo;
    b = a + width - 1;
  }}

  if (b > hi) {{
    b = hi;
    a = b - width + 1;
  }}

  return {{ start: a, end: b }};
}}

function applyLensHandleDrag(evt) {{
  if (!activeLensHandleDrag) return;

  const s = state();

  const isGlobal = activeLensHandleDrag.kind === "global";
  const isBasin = activeLensHandleDrag.kind === "basin";
  const bar = isGlobal ? globalBar : focusBar;
  const rect = bar.getBoundingClientRect();

  const domainStart = isGlobal ? 1 : s.start;
  const domainEnd = isGlobal ? data.max_line : s.end;

  const lineDomain = isGlobal ? data.max_line : Math.max(1, s.end - s.start + 1);
  const delta = Math.round(((evt.clientX - activeLensHandleDrag.mouseStart) / Math.max(1, rect.width)) * lineDomain);

  let a = activeLensHandleDrag.start;
  let b = activeLensHandleDrag.end;

  if (activeLensHandleDrag.mode === "move") {{
    const moved = moveRangeByDelta(a, b, delta, domainStart, domainEnd);
    a = moved.start;
    b = moved.end;
  }}

  if (activeLensHandleDrag.mode === "left") {{
    a = clamp(activeLensHandleDrag.start + delta, domainStart, b - 1);
  }}

  if (activeLensHandleDrag.mode === "right") {{
    b = clamp(activeLensHandleDrag.end + delta, a + 1, domainEnd);
  }}

  if (isGlobal) {{
    spanDial.value = clamp(b - a + 1, parseInt(spanDial.min), parseInt(spanDial.max));
    centerDial.value = clamp(Math.round((a + b) / 2), 1, data.max_line);
    render();
    return;
  }}

  if (isBasin) {{
    basinStart = a;
    basinEnd = b;

    if (inspectionStart !== null && inspectionEnd !== null) {{
      inspectionStart = clamp(inspectionStart, basinStart, basinEnd);
      inspectionEnd = clamp(inspectionEnd, basinStart, basinEnd);
      if (inspectionEnd < inspectionStart) {{
        inspectionStart = basinStart;
        inspectionEnd = basinEnd;
      }}
      deriveApertureFromInspection();
      renderInspectionPreviewOnly();
    }}

    render();
    return;
  }}

  inspectionStart = clamp(a, basinStart !== null ? basinStart : s.start, basinEnd !== null ? basinEnd : s.end);
  inspectionEnd = clamp(b, basinStart !== null ? basinStart : s.start, basinEnd !== null ? basinEnd : s.end);

  for (let i = inspectionStart; i <= inspectionEnd; i++) {{
    isLineIncluded(i);
  }}

  deriveApertureFromInspection();
  renderInspectionPreviewOnly();
  render();
}}

document.addEventListener("mousemove", evt => {{
  applyLensHandleDrag(evt);
}});

document.addEventListener("mouseup", evt => {{
  activeLensHandleDrag = null;
}});


function lensProfileY(idx) {{
  if (data.sizes.length <= 1) return 0;

  const minLog = Math.log(data.sizes[0]);
  const maxLog = Math.log(data.sizes[data.sizes.length - 1]);
  const v = Math.log(data.sizes[idx]);

  return ((v - minLog) / Math.max(0.0001, maxLog - minLog)) * 100;
}}

function ensureLensProfile(kind, bar, dial) {{
  const id = kind === "global" ? "globalLensProfile" : "focusLensProfile";
  if (document.getElementById(id)) return;

  const row = document.createElement("div");
  row.className = "lensProfileRow";
  row.id = id + "Row";

  const profile = document.createElement("div");
  profile.className = "lensProfile";
  profile.id = id;

  const value = document.createElement("div");
  value.className = "lensProfileValue";
  value.id = id + "Value";
  profile.appendChild(value);

  data.sizes.forEach((size, idx) => {{
    const step = document.createElement("div");
    step.className = "lensProfileStep";
    step.setAttribute("data-index", idx);
    step.style.top = lensProfileY(idx) + "%";

    const mark = document.createElement("div");
    mark.className = "lensProfileMark";

    const pct = data.sizes.length <= 1 ? 1 : idx / (data.sizes.length - 1);
    mark.style.width = (9 + pct * 46) + "px";

    step.appendChild(mark);
    profile.appendChild(step);
  }});

  bar.parentNode.insertBefore(row, bar);
  row.appendChild(profile);
  row.appendChild(bar);

  function indexFromMouse(evt) {{
    const rect = profile.getBoundingClientRect();
    const y = clamp(evt.clientY - rect.top, 0, rect.height);
    const pct = y / Math.max(1, rect.height);

    let bestIdx = 0;
    let bestDist = 999;

    data.sizes.forEach((size, idx) => {{
      const yp = lensProfileY(idx) / 100;
      const d = Math.abs(yp - pct);
      if (d < bestDist) {{
        bestDist = d;
        bestIdx = idx;
      }}
    }});

    return bestIdx;
  }}

  let draggingProfile = false;

  function setProfileIndex(idx) {{
    dial.value = clamp(idx, parseInt(dial.min), parseInt(dial.max));

    if (kind === "global") {{
    }}

    render();
  }}

  profile.addEventListener("mousedown", evt => {{
    draggingProfile = true;
    setProfileIndex(indexFromMouse(evt));
  }});

  profile.addEventListener("mousemove", evt => {{
    if (!draggingProfile) return;
    setProfileIndex(indexFromMouse(evt));
  }});

  document.addEventListener("mouseup", evt => {{
    draggingProfile = false;
  }});

  profile.addEventListener("wheel", evt => {{
    evt.preventDefault();
    evt.stopPropagation();

    let idx = parseInt(dial.value);
    idx = evt.deltaY > 0 ? idx + 1 : idx - 1;
    setProfileIndex(idx);
  }}, {{ passive:false }});
}}

function updateLensProfile(kind, dial) {{
  const id = kind === "global" ? "globalLensProfile" : "focusLensProfile";
  const profile = document.getElementById(id);
  const value = document.getElementById(id + "Value");
  if (!profile || !value) return;

  const active = parseInt(dial.value);
  value.textContent = data.sizes[active];

  profile.querySelectorAll(".lensProfileStep").forEach(step => {{
    const idx = parseInt(step.getAttribute("data-index"));
    step.classList.toggle("active", idx === active);
  }});
}}

function ensureLensProfiles() {{
  ensureLensProfile("global", globalBar, globalSizeDial);
  ensureLensProfile("focus", focusBar, focusSizeDial);
}}

function updateLensProfiles() {{
  updateLensProfile("global", globalSizeDial);
  updateLensProfile("focus", focusSizeDial);
}}


/* SECTION 8 — GLOBAL INTERACTION */
globalBar.addEventListener("mousedown", evt => {{
  dragging = true;
  dragStartLine = lineFromMouse(evt, globalBar, 1, data.max_line);

  if (dragBox) {{ dragBox.remove(); }}

  dragBox = document.createElement("div");
  dragBox.className = "dragBox";
  globalBar.appendChild(dragBox);
}});

globalBar.addEventListener("mousemove", evt => {{
  if (!dragging || !dragBox) return;

  const currentLine = lineFromMouse(evt, globalBar, 1, data.max_line);
  const a = Math.min(dragStartLine, currentLine);
  const b = Math.max(dragStartLine, currentLine);

  dragBox.style.left = ((a - 1) / data.max_line * 100) + "%";
  dragBox.style.width = ((b - a + 1) / data.max_line * 100) + "%";
}});

globalBar.addEventListener("mouseup", evt => {{
  if (!dragging) return;

  dragging = false;

  const endLine = lineFromMouse(evt, globalBar, 1, data.max_line);
  const a = Math.min(dragStartLine, endLine);
  const b = Math.max(dragStartLine, endLine);

  const span = Math.max(500, b - a + 1);
  const center = Math.round((a + b) / 2);

  spanDial.value = clamp(span, parseInt(spanDial.min), parseInt(spanDial.max));
  centerDial.value = clamp(center, 1, data.max_line);

  if (dragBox) {{ dragBox.remove(); dragBox = null; }}
  render();
}});

globalBar.addEventListener("wheel", evt => {{
  evt.preventDefault();

  let idx = parseInt(globalSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  globalSizeDial.value = clamp(idx, parseInt(globalSizeDial.min), parseInt(globalSizeDial.max));
  render();
}});

focusBar.addEventListener("wheel", evt => {{
  evt.preventDefault();

  let idx = parseInt(focusSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  focusSizeDial.value = clamp(idx, parseInt(focusSizeDial.min), parseInt(focusSizeDial.max));
  render();
}});

/* SECTION 9 — FOCUS INTERACTION */
focusBar.addEventListener("mousedown", evt => {{
  focusDragging = true;

  const s = state();
  focusDragStartLine = lineFromMouse(evt, focusBar, s.start, s.end);

  if (focusDragBox) {{ focusDragBox.remove(); }}

  focusDragBox = document.createElement("div");
  focusDragBox.className = "dragBox";
  focusBar.appendChild(focusDragBox);
}});

focusBar.addEventListener("mousemove", evt => {{
  if (!focusDragging || !focusDragBox) return;

  const s = state();
  const currentLine = lineFromMouse(evt, focusBar, s.start, s.end);
  const a = Math.min(focusDragStartLine, currentLine);
  const b = Math.max(focusDragStartLine, currentLine);

  focusDragBox.style.left = ((a - s.start) / (s.end - s.start + 1) * 100) + "%";
  focusDragBox.style.width = ((b - a + 1) / (s.end - s.start + 1) * 100) + "%";
}});

focusBar.addEventListener("mouseup", evt => {{
  if (!focusDragging) return;

  focusDragging = false;

  const s = state();
  const endLine = lineFromMouse(evt, focusBar, s.start, s.end);
  const a = Math.min(focusDragStartLine, endLine);
  const b = Math.max(focusDragStartLine, endLine);

  if (Math.abs(b - a) < 3) {{
    previewLines(a);
  }} else if (basinContains(a, b)) {{
    setInspectionRange(a, b);
    renderInspectionPreviewOnly();
    render();
  }} else {{
    if (basinContains(a, b)) {{
      previewInspectionRange(a, b);
    }} else {{
      previewLineRange(a, b);
    }}
  }}

  if (focusDragBox) {{
    focusDragBox.remove();
    focusDragBox = null;
  }}
}});

focusBar.addEventListener("mouseleave", evt => {{
  if (focusDragging) {{
    focusDragging = false;
    if (focusDragBox) {{
      focusDragBox.remove();
      focusDragBox = null;
    }}
  }}
}});

globalSizeDial.addEventListener("input", evt => {{
  render();
}});

[focusSizeDial, spanDial, centerDial].forEach(el => {{
  el.addEventListener("input", render);
}});


function refreshSelectionViews() {{
  renderEvidenceMicroBars(state());
  renderRawRowsForCurrentState();
}}

function allLinesMatchingRuleAreIncluded(rule) {{
  if (apertureStart === null || apertureEnd === null) return false;

  const s = state();
  let seen = false;

  for (let i = apertureStart; i <= apertureEnd; i++) {{
    const part = dominantPartForLine(i, s);

    const matches =
      rule === "all" ||
      (rule === "stable" && part === "stable") ||
      (rule === "middle" && part === "middle") ||
      (rule === "residual" && part === "residual");

    if (!matches) continue;

    seen = true;
    if (!isLineIncluded(i)) return false;
  }}

  return seen;
}}

function applySelectionRuleToFocus(rule) {{
  if (apertureStart === null || apertureEnd === null) {{
    csvStatus.textContent = "No focus center selected.";
    return;
  }}

  const s = state();
  const shouldInclude = !allLinesMatchingRuleAreIncluded(rule);

  for (let i = apertureStart; i <= apertureEnd; i++) {{
    const part = dominantPartForLine(i, s);

    if (rule === "all") {{
      setLineIncluded(i, shouldInclude);
    }}

    if (rule === "none") {{
      setLineIncluded(i, false);
    }}

    if (rule === "stable" && part === "stable") {{
      setLineIncluded(i, shouldInclude);
    }}

    if (rule === "middle" && part === "middle") {{
      setLineIncluded(i, shouldInclude);
    }}

    if (rule === "residual" && part === "residual") {{
      setLineIncluded(i, shouldInclude);
    }}
  }}

  csvStatus.textContent =
    (shouldInclude ? "Selected " : "Deselected ") + rule + " in focus center.";

  refreshSelectionViews();
}}

function csvEscape(value) {{
  const s = String(value === null || value === undefined ? "" : value);
  return '"' + s.replace(/"/g, '""') + '"';
}}

function rowsForCsvRange(kind, startLine, endLine) {{
  const rows = [];

  if (startLine === null || endLine === null) return rows;

  const s = state();

  for (let i = startLine; i <= endLine; i++) {{
    if (!isLineIncluded(i)) continue;

    rows.push({{
      source_kind: kind,
      terrain: "Imported_Terrain",
      line_number: i,
      line_text: data.source_lines[i - 1] || "",
      global_window: s.globalSize,
      focus_window: s.focusSize,
      global_start: s.start,
      global_end: s.end,
      basin_start: basinStart,
      basin_end: basinEnd,
      inspection_start: inspectionStart,
      inspection_end: inspectionEnd,
      aperture_start: apertureStart,
      aperture_end: apertureEnd,
      note: noteText.value || "",
      unresolved: unresolvedText.value || ""
    }});
  }}

  return rows;
}}

function saveCsvPacket(kind, startLine, endLine) {{
  const rows = rowsForCsvRange(kind, startLine, endLine);

  if (rows.length === 0) {{
    csvStatus.textContent = "No included rows to save.";
    return;
  }}

  csvPackets.push({{
    packet_id: "packet_" + Date.now(),
    created_local: new Date().toISOString(),
    kind: kind,
    rows: rows
  }});

  csvStatus.textContent =
    "Saved " + kind + " CSV packet " + csvPackets.length + " with " + rows.length + " row(s).";

  renderCsvPacketSurface();
}}


function countIncludedRowsForBookmark(bookmark) {{
  let count = 0;
  const mask = bookmark.selection_mask || {{}};

  if (bookmark.inspection_start === null || bookmark.inspection_end === null) {{
    return 0;
  }}

  for (let i = parseInt(bookmark.inspection_start); i <= parseInt(bookmark.inspection_end); i++) {{
    if (mask[String(i)] !== false) count += 1;
  }}

  return count;
}}

function rowsForBookmarkCsv(bookmark) {{
  const rows = [];
  const mask = bookmark.selection_mask || {{}};

  if (bookmark.inspection_start === null || bookmark.inspection_end === null) {{
    return rows;
  }}

  for (let i = parseInt(bookmark.inspection_start); i <= parseInt(bookmark.inspection_end); i++) {{
    if (mask[String(i)] === false) continue;

    rows.push({{
      source_kind: "saved_card",
      terrain: bookmark.terrain || "Imported_Terrain",
      line_number: i,
      line_text: data.source_lines[i - 1] || "",
      global_window: bookmark.global_window,
      focus_window: bookmark.focus_window,
      global_start: bookmark.focus_start,
      global_end: bookmark.focus_end,
      basin_start: bookmark.basin_start,
      basin_end: bookmark.basin_end,
      inspection_start: bookmark.inspection_start,
      inspection_end: bookmark.inspection_end,
      aperture_start: bookmark.aperture_start,
      aperture_end: bookmark.aperture_end,
      note: bookmark.operator_note || "",
      unresolved: bookmark.unresolved_status || ""
    }});
  }}

  return rows;
}}

function saveBookmarkCsvPacket(bookmark) {{
  const rows = rowsForBookmarkCsv(bookmark);

  if (rows.length === 0) {{
    csvStatus.textContent = "No included rows on this card.";
    return;
  }}

  csvPackets.push({{
    packet_id: "card_packet_" + Date.now(),
    created_local: new Date().toISOString(),
    kind: "saved_card",
    rows: rows
  }});

  csvStatus.textContent =
    "Saved card CSV packet with " + rows.length + " row(s).";

  renderCsvPacketSurface();
}}


function ensureDefaultPack() {{
  if (cardPacks.length === 0) {{
    cardPacks.push({{
      pack_id: "pack_" + Date.now(),
      name: "Pack 1",
      cards: []
    }});
    activePackIndex = 0;
  }}
}}

function activePack() {{
  ensureDefaultPack();
  return cardPacks[activePackIndex];
}}

function renderCardPackSurface() {{
  if (!cardPackList) return;

  ensureDefaultPack();

  cardPackList.innerHTML = "";

  cardPacks.forEach((pack, packIdx) => {{
    const box = document.createElement("div");
    box.style.border = packIdx === activePackIndex ? "2px solid #1f66d1" : "1px solid #bbb";
    box.style.padding = "8px";
    box.style.marginBottom = "8px";
    box.style.background = packIdx === activePackIndex ? "#eef5ff" : "white";

    const title = document.createElement("div");
    title.innerHTML =
      "<b>" + pack.name + "</b> " +
      "<span style='color:#666;'>(" + pack.cards.length + " card(s))</span>";

    const buttons = document.createElement("div");
    buttons.style.marginTop = "6px";

    const activate = document.createElement("button");
    activate.textContent = "make active";
    activate.style.fontSize = "12px";
    activate.addEventListener("click", evt => {{
      activePackIndex = packIdx;
      renderCardPackSurface();
    }});

    const savePack = document.createElement("button");
    savePack.textContent = "save pack to CSV";
    savePack.style.fontSize = "12px";
    savePack.style.marginLeft = "6px";
    savePack.addEventListener("click", evt => {{
      saveCardPackCsvPacket(pack);
    }});

    const clearPack = document.createElement("button");
    clearPack.textContent = "clear pack";
    clearPack.style.fontSize = "12px";
    clearPack.style.marginLeft = "6px";
    clearPack.addEventListener("click", evt => {{
      pack.cards = [];
      renderCardPackSurface();
      bookmarkPreview.textContent = "pack cleared: " + pack.name;
    }});

    buttons.appendChild(activate);
    buttons.appendChild(savePack);
    buttons.appendChild(clearPack);

    const cards = document.createElement("div");
    cards.style.marginTop = "8px";

    if (pack.cards.length === 0) {{
      cards.innerHTML = "<div style='color:#666;'>No cards in this pack.</div>";
    }} else {{
      pack.cards.forEach((bookmark, idx) => {{
        const div = document.createElement("div");
        div.style.borderTop = "1px solid #ddd";
        div.style.paddingTop = "5px";
        div.style.marginTop = "5px";
        div.innerHTML =
          "<b>" + (bookmark.card_label || ("card " + (idx + 1))) + "</b><br>" +
          "basin: " + bookmark.basin_start + "-" + bookmark.basin_end + "<br>" +
          "inspection: " + bookmark.inspection_start + "-" + bookmark.inspection_end + "<br>" +
          "saved logs: " + countIncludedRowsForBookmark(bookmark) + "<br>" +
          "note: " + (bookmark.operator_note || "");
        cards.appendChild(div);
      }});
    }}

    box.appendChild(title);
    box.appendChild(buttons);
    box.appendChild(cards);
    cardPackList.appendChild(box);
  }});
}}

function createNamedCardPack() {{
  const name = (newPackName.value || "").trim() || ("Pack " + (cardPacks.length + 1));

  cardPacks.push({{
    pack_id: "pack_" + Date.now(),
    name: name,
    cards: []
  }});

  activePackIndex = cardPacks.length - 1;
  newPackName.value = "";
  renderCardPackSurface();
}}

function addBookmarkToCurrentPack(bookmark) {{
  const pack = activePack();

  const exists = pack.cards.some(b => b.bookmark_id === bookmark.bookmark_id);
  if (!exists) pack.cards.push(bookmark);

  renderCardPackSurface();
  bookmarkPreview.textContent =
    (bookmark.card_label || "card") + " added to " + pack.name;
}}

function saveCardPackCsvPacket(pack) {{
  let rows = [];

  pack.cards.forEach(bookmark => {{
    const cardRows = rowsForBookmarkCsv(bookmark);
    cardRows.forEach(row => {{
      row.source_kind = "card_pack";
      row.pack_name = pack.name;
      row.card_label = bookmark.card_label || "";
      rows.push(row);
    }});
  }});

  if (rows.length === 0) {{
    csvStatus.textContent = "No included rows in pack: " + pack.name;
    return;
  }}

  csvPackets.push({{
    packet_id: "pack_packet_" + Date.now(),
    created_local: new Date().toISOString(),
    kind: "card_pack",
    rows: rows
  }});

  csvStatus.textContent =
    "Saved pack CSV packet '" + pack.name + "' with " + rows.length + " row(s).";

  renderCsvPacketSurface();
}}


function renderCsvPacketSurface() {{
  if (!csvPacketList) return;

  csvPacketList.innerHTML = "";

  if (csvPackets.length === 0) {{
    csvPacketList.innerHTML =
      '<div style="color:#666;">No CSV packets saved.</div>';
    return;
  }}

  csvPackets.forEach((packet, idx) => {{
    const div = document.createElement("div");

    div.style.border = "1px solid #bbb";
    div.style.padding = "6px";
    div.style.marginBottom = "6px";
    div.style.background = "white";

    div.innerHTML =
      "<b>packet " + (idx + 1) + "</b><br>" +
      "kind: " + packet.kind + "<br>" +
      "rows: " + packet.rows.length + "<br>" +
      "created: " + packet.created_local;

    csvPacketList.appendChild(div);
  }});
}}


function buildCsvText() {{
  const header = [
    "packet_id",
    "created_local",
    "source_kind",
    "pack_name",
    "card_label",
    "terrain",
    "line_number",
    "line_text",
    "global_window",
    "focus_window",
    "global_start",
    "global_end",
    "basin_start",
    "basin_end",
    "inspection_start",
    "inspection_end",
    "aperture_start",
    "aperture_end",
    "note",
    "unresolved"
  ];

  const out = [header.join(",")];

  csvPackets.forEach(packet => {{
    packet.rows.forEach(row => {{
      out.push([
        packet.packet_id,
        packet.created_local,
        row.source_kind,
        row.pack_name || "",
        row.card_label || "",
        row.terrain,
        row.line_number,
        row.line_text,
        row.global_window,
        row.focus_window,
        row.global_start,
        row.global_end,
        row.basin_start,
        row.basin_end,
        row.inspection_start,
        row.inspection_end,
        row.aperture_start,
        row.aperture_end,
        row.note,
        row.unresolved
      ].map(csvEscape).join(","));
    }});
  }});

  return out.join("\\n");
}}

function downloadCsvPackets() {{
  if (csvPackets.length === 0) {{
    csvStatus.textContent = "No CSV packets saved yet.";
    return;
  }}

  const blob = new Blob([buildCsvText()], {{ type: "text/csv;charset=utf-8" }});
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "selected_evidence_packets.csv";
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);
  csvStatus.textContent = "Downloaded " + csvPackets.length + " CSV packet(s).";
}}

function clearAllCsvPackets() {{
  csvPackets = [];
  renderCsvPacketSurface();
  csvStatus.textContent = "CSV packets cleared.";
}}


function wireCsvAndSelectionInteraction() {{
  createCardPack.addEventListener("click", evt => {{
    createNamedCardPack();
  }});



  selectAllFocus.addEventListener("click", evt => {{
    applySelectionRuleToFocus("all");
  }});

  deselectAllFocus.addEventListener("click", evt => {{
    applySelectionRuleToFocus("none");
  }});

  selectWhiteFocus.addEventListener("click", evt => {{
    applySelectionRuleToFocus("stable");
  }});

  selectGreyFocus.addEventListener("click", evt => {{
    applySelectionRuleToFocus("middle");
  }});

  selectBlackFocus.addEventListener("click", evt => {{
    applySelectionRuleToFocus("residual");
  }});

  saveBrownCsv.addEventListener("click", evt => {{
    saveCsvPacket("brown_basin", basinStart, basinEnd);
  }});

  saveGreenCsv.addEventListener("click", evt => {{
    saveCsvPacket("green_inspection", inspectionStart, inspectionEnd);
  }});

  saveApertureCsv.addEventListener("click", evt => {{
    saveCsvPacket("focus_center", apertureStart, apertureEnd);
  }});

  downloadCsv.addEventListener("click", evt => {{
    downloadCsvPackets();
  }});

  clearCsvPackets.addEventListener("click", evt => {{
    clearAllCsvPackets();
  }});
}}



function compactCsvControls() {{
  const controls = document.getElementById("csvSelectionControls");
  if (!controls) return;

  const all = document.getElementById("selectAllFocus");
  const white = document.getElementById("selectWhiteFocus");
  const grey = document.getElementById("selectGreyFocus");
  const black = document.getElementById("selectBlackFocus");
  const green = document.getElementById("saveGreenCsv");
  const focus = document.getElementById("saveApertureCsv");
  const download = document.getElementById("downloadCsv");
  const clear = document.getElementById("clearCsvPackets");

  if (all) all.textContent = "all";
  if (white) white.textContent = "white";
  if (grey) grey.textContent = "grey";
  if (black) black.textContent = "black";
  const brown = document.getElementById("saveBrownCsv");

  if (brown) brown.textContent = "save brown";
  if (green) green.textContent = "save green";
  if (focus) focus.textContent = "save focus";
  if (download) download.textContent = "download";
  if (clear) clear.textContent = "clear packets";

  let pad = document.getElementById("selectionPad");
  if (!pad) {{
    pad = document.createElement("div");
    pad.id = "selectionPad";

    [all, white, grey, black].forEach(btn => {{
      if (btn) pad.appendChild(btn);
    }});

    controls.insertBefore(pad, controls.firstChild);
  }}

  let csvGroup = controls.querySelector(".csvControlGroup");
  if (!csvGroup) {{
    csvGroup = document.createElement("div");
    csvGroup.className = "csvControlGroup";

    const title = document.createElement("div");
    title.className = "csvTitle";
    title.textContent = "CSV";

    const saveRow = document.createElement("div");
    saveRow.className = "csvSaveRow";

    const actionRow = document.createElement("div");
    actionRow.className = "csvActionRow";

    if (brown) {{
      brown.classList.add("csvBrownButton");
      saveRow.appendChild(brown);
    }}

    if (green) {{
      green.classList.add("csvGreenButton");
      saveRow.appendChild(green);
    }}

    if (focus) {{
      focus.classList.add("csvFocusButton");
      saveRow.appendChild(focus);
    }}

    if (download) actionRow.appendChild(download);
    if (clear) actionRow.appendChild(clear);

    csvGroup.appendChild(title);
    csvGroup.appendChild(saveRow);
    csvGroup.appendChild(actionRow);
    controls.appendChild(csvGroup);
  }}
}}

function ensureLowerWorkbenchLayout() {{
  if (document.getElementById("lowerWorkbench")) return;

  const controls = document.getElementById("csvSelectionControls");
  const packets = document.getElementById("csvPacketSurface");
  const line = document.getElementById("linePreview");
  const sticky = noteText ? noteText.closest(".box") : null;

  if (!controls || !line || !sticky) return;

  const workbench = document.createElement("div");
  workbench.id = "lowerWorkbench";

  const left = document.createElement("div");
  left.id = "lowerLeftPanel";

  const right = document.createElement("div");
  right.id = "lowerRightPanel";

  line.parentNode.insertBefore(workbench, line);

  left.appendChild(controls);
  if (packets) left.appendChild(packets);

  right.appendChild(line);
  right.appendChild(sticky);

  workbench.appendChild(left);
  workbench.appendChild(right);
}}

function layoutRefineOnce() {{
  compactCsvControls();
  ensureLowerWorkbenchLayout();
}}


function ensureFocusLabelBand() {{
  let band = document.getElementById("focusFrameLabelBand");
  if (band) return band;

  band = document.createElement("div");
  band.id = "focusFrameLabelBand";
  focusBar.parentNode.insertBefore(band, focusBar.nextSibling);
  return band;
}}

function ensureFrameCountSummary() {{
  let summary = document.getElementById("frameCountSummary");
  if (summary) return summary;

  summary = document.createElement("div");
  summary.id = "frameCountSummary";
  const band = ensureFocusLabelBand();
  band.parentNode.insertBefore(summary, band.nextSibling);
  return summary;
}}

function pctForFocusLine(line, s) {{
  const span = Math.max(1, s.end - s.start + 1);
  const clamped = clamp(line, s.start, s.end);
  return ((clamped - s.start) / span) * 100;
}}

function addFrameBottomLabel(band, cls, pct, textValue) {{
  const label = document.createElement("div");
  label.className = "frameBottomLabel " + cls;
  label.style.left = pct + "%";
  label.textContent = textValue;
  band.appendChild(label);
}}

function renderFocusBottomLabelsAndCounts() {{
  const s = state();
  const band = ensureFocusLabelBand();
  const summary = ensureFrameCountSummary();

  band.innerHTML = "";

  if (basinStart !== null && basinEnd !== null) {{
    addFrameBottomLabel(band, "brown", pctForFocusLine(basinStart, s), basinStart);
    addFrameBottomLabel(band, "brown", pctForFocusLine(basinEnd, s), basinEnd);
  }}

  if (inspectionStart !== null && inspectionEnd !== null) {{
    addFrameBottomLabel(band, "green", pctForFocusLine(inspectionStart, s), inspectionStart);
    addFrameBottomLabel(band, "green", pctForFocusLine(inspectionEnd, s), inspectionEnd);

    const greenCenter = Math.round((inspectionStart + inspectionEnd) / 2);
    addFrameBottomLabel(band, "green", pctForFocusLine(greenCenter, s), greenCenter);
  }}

  if (apertureStart !== null && apertureEnd !== null) {{
    const apertureCenter = Math.round((apertureStart + apertureEnd) / 2);
    addFrameBottomLabel(band, "blue", pctForFocusLine(apertureCenter, s), apertureCenter);
  }}

  const brownCount =
    basinStart !== null && basinEnd !== null ? (basinEnd - basinStart + 1) : 0;

  const greenCount =
    inspectionStart !== null && inspectionEnd !== null ? (inspectionEnd - inspectionStart + 1) : 0;

  const focalCount =
    apertureStart !== null && apertureEnd !== null ? (apertureEnd - apertureStart + 1) : 0;

  summary.innerHTML =
    "<span class='brown'>brown " + brownCount + "</span>" +
    "<span class='green'>green " + greenCount + "</span>" +
    "<span class='blue'>focus " + focalCount + "</span>";
}}

function ensureProjectionLayer() {{
  let svg = document.getElementById("projectionLayer");
  if (svg) return svg;

  svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.id = "projectionLayer";
  document.body.appendChild(svg);
  return svg;
}}

function addProjectionLine(svg, x1, y1, x2, y2, color) {{
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1);
  line.setAttribute("y1", y1);
  line.setAttribute("x2", x2);
  line.setAttribute("y2", y2);
  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", "3.0");
  line.setAttribute("opacity", "0.68");
  svg.appendChild(line);
}}

function renderProjectionLines() {{
  const svg = ensureProjectionLayer();
  svg.innerHTML = "";

  const globalLens = globalBar.querySelector(".lens");
  if (globalLens) {{
    const g = globalLens.getBoundingClientRect();
    const f = focusBar.getBoundingClientRect();

    addProjectionLine(svg, g.left, g.bottom, f.left, f.top, "#2f5f8f");
    addProjectionLine(svg, g.right, g.bottom, f.right, f.top, "#2f5f8f");
  }}

  const aperture = focusBar.querySelector(".apertureFrame");
  const micro = document.getElementById("evidenceMicroBars");

  if (aperture && micro) {{
    const a = aperture.getBoundingClientRect();
    const m = micro.getBoundingClientRect();

    addProjectionLine(svg, a.left, a.bottom, m.left, m.top, "#d9b43a");
    addProjectionLine(svg, a.right, a.bottom, m.right, m.top, "#d9b43a");
  }}
}}

let projectionRefreshQueued = false;

function queueProjectionRefresh() {{
  if (projectionRefreshQueued) return;

  projectionRefreshQueued = true;
  requestAnimationFrame(() => {{
    projectionRefreshQueued = false;
    renderFocusBottomLabelsAndCounts();
    renderProjectionLines();
  }});
}}

window.addEventListener("scroll", queueProjectionRefresh, true);
window.addEventListener("resize", queueProjectionRefresh);


function hideOldContextStatusLineSafe() {{
  document.querySelectorAll("div, span, p").forEach(el => {{
    const t = (el.textContent || "").trim();

    if (
      t.length < 180 &&
      t.includes("green inspection:") &&
      t.includes("focal aperture:") &&
      t.includes("brown saving:")
    ) {{
      el.style.display = "none";
    }}
  }});
}}


function forceV54DVisuals() {{
  document.querySelectorAll(".apertureFrame").forEach(frame => {{
    frame.style.background = "rgba(247, 222, 132, 0.26)";
    frame.style.borderLeft = "2px solid #d9b43a";
    frame.style.borderRight = "2px solid #d9b43a";
    frame.style.borderTop = "1px solid #d9b43a";
    frame.style.borderBottom = "1px solid #d9b43a";
    frame.style.boxShadow = "inset 0 0 0 1px rgba(175,135,20,0.25)";
  }});

  document.querySelectorAll("div, span, p").forEach(el => {{
    const t = (el.textContent || "").trim();

    if (
      t.length < 220 &&
      t.includes("green inspection:") &&
      t.includes("focal aperture:") &&
      t.includes("brown saving:")
    ) {{
      el.style.display = "none";
    }}
  }});
}}


function enforceMinimumNestedFrames() {{
  if (apertureStart === null || apertureEnd === null) return;

  const margin = 17;

  let nextInspectionStart = inspectionStart;
  let nextInspectionEnd = inspectionEnd;
  let nextBasinStart = basinStart;
  let nextBasinEnd = basinEnd;

  if (inspectionStart !== null && inspectionEnd !== null) {{
    nextInspectionStart = Math.min(nextInspectionStart, apertureStart - margin);
    nextInspectionEnd = Math.max(nextInspectionEnd, apertureEnd + margin);
  }}

  if (basinStart !== null && basinEnd !== null) {{
    nextBasinStart = Math.min(nextBasinStart, nextInspectionStart - margin);
    nextBasinEnd = Math.max(nextBasinEnd, nextInspectionEnd + margin);
  }}

  const s = state();

  if (nextInspectionStart !== null && nextInspectionEnd !== null) {{
    inspectionStart = clamp(nextInspectionStart, s.start, s.end);
    inspectionEnd = clamp(nextInspectionEnd, s.start, s.end);
  }}

  if (nextBasinStart !== null && nextBasinEnd !== null) {{
    basinStart = clamp(nextBasinStart, s.start, s.end);
    basinEnd = clamp(nextBasinEnd, s.start, s.end);
  }}
}}

function forceV54ELayout() {{
  enforceMinimumNestedFrames();

  document.querySelectorAll(".pointLabel").forEach(el => {{
    el.style.display = "none";
  }});
}}


function forceV54F2Visuals() {{
  document.querySelectorAll(".apertureFrame").forEach(frame => {{
    frame.style.background = "rgba(150, 205, 235, 0.24)";
    frame.style.borderLeft = "2px solid #5f9fc8";
    frame.style.borderRight = "2px solid #5f9fc8";
    frame.style.borderTop = "1px solid #5f9fc8";
    frame.style.borderBottom = "1px solid #5f9fc8";
    frame.style.boxShadow = "inset 0 0 0 1px rgba(75,130,165,0.25)";
  }});
}}

function refineNoteCardLayout() {{
  if (document.getElementById("noteCardRow")) return;

  const sticky = noteText ? noteText.closest(".box") : null;
  const cards = document.getElementById("bookmarkCards");
  const packs = document.getElementById("cardPackSurface");

  if (!sticky || !cards || !sticky.parentNode) return;

  const row = document.createElement("div");
  row.id = "noteCardRow";

  sticky.parentNode.insertBefore(row, sticky);
  row.appendChild(sticky);
  row.appendChild(cards);

  if (packs) {{
    row.parentNode.insertBefore(packs, row.nextSibling);
  }}
}}


function forceV54GFinalVisuals() {{
  document.querySelectorAll(".apertureFrame").forEach(frame => {{
    frame.style.background = "rgba(150, 205, 235, 0.24)";
    frame.style.borderLeft = "2px solid #5f9fc8";
    frame.style.borderRight = "2px solid #5f9fc8";
    frame.style.borderTop = "1px solid #5f9fc8";
    frame.style.borderBottom = "1px solid #5f9fc8";
    frame.style.boxShadow = "inset 0 0 0 1px rgba(75,130,165,0.25)";
  }});

  document.querySelectorAll(".pointLabel").forEach(el => {{
    el.style.display = "none";
  }});
}}


function forceV54G1Tighten() {{
  document.querySelectorAll(".framePointLabel").forEach(el => {{
    el.style.display = "none";
  }});

  if (linePreviewLabel) {{
    linePreviewLabel.style.display = "none";
  }}

  document.querySelectorAll(".apertureFrame").forEach(frame => {{
    frame.style.setProperty("background", "rgba(150, 205, 235, 0.24)", "important");
    frame.style.setProperty("border-left", "2px solid #5f9fc8", "important");
    frame.style.setProperty("border-right", "2px solid #5f9fc8", "important");
    frame.style.setProperty("border-top", "1px solid #5f9fc8", "important");
    frame.style.setProperty("border-bottom", "1px solid #5f9fc8", "important");
    frame.style.setProperty("box-shadow", "inset 0 0 0 1px rgba(75,130,165,0.25)", "important");
  }});

  const sticky = noteText ? noteText.closest(".box") : null;
  if (sticky) {{
    sticky.classList.add("stickyNoteBox");
    const title = sticky.querySelector("div");
    if (title) title.textContent = "Sticky note";
  }}
}}


function forceV54G2ColorShift() {{
  document.querySelectorAll(".inspectionFrame").forEach(frame => {{
    frame.style.setProperty("background", "rgba(140,195,230,0.18)", "important");
    frame.style.setProperty("border-left", "5px solid #4f8fbd", "important");
    frame.style.setProperty("border-right", "5px solid #4f8fbd", "important");
    frame.style.setProperty("border-top", "2px solid #4f8fbd", "important");
    frame.style.setProperty("border-bottom", "2px solid #4f8fbd", "important");
  }});

  document.querySelectorAll(".apertureFrame").forEach(frame => {{
    frame.style.setProperty("background", "rgba(247,222,132,0.30)", "important");
    frame.style.setProperty("border-left", "2px solid #d9b43a", "important");
    frame.style.setProperty("border-right", "2px solid #d9b43a", "important");
    frame.style.setProperty("border-top", "1px solid #d9b43a", "important");
    frame.style.setProperty("border-bottom", "1px solid #d9b43a", "important");
    frame.style.setProperty("box-shadow", "inset 0 0 0 1px rgba(175,135,20,0.25)", "important");
  }});

  const saveGreen = document.getElementById("saveGreenCsv");
  if (saveGreen) {{
    saveGreen.textContent = "save blue";
    saveGreen.classList.add("csvGreenButton");
  }}

  const saveFocus = document.getElementById("saveApertureCsv");
  if (saveFocus) {{
    saveFocus.textContent = "save focus";
    saveFocus.classList.add("csvFocusButton");
  }}

  const summary = document.getElementById("frameCountSummary");
  if (summary) {{
    summary.innerHTML = summary.innerHTML.replace("green ", "blue ");
  }}
}}


function renderV54G3BSafeLabels() {{
  if (
    typeof ensureFocusLabelBand !== "function" ||
    typeof ensureFrameCountSummary !== "function" ||
    typeof pctForFocusLine !== "function"
  ) {{
    return;
  }}

  const s = state();
  const band = ensureFocusLabelBand();
  const summary = ensureFrameCountSummary();

  band.innerHTML = "";

  if (typeof addFrameBottomLabel === "function") {{
    if (basinStart !== null && basinEnd !== null) {{
      addFrameBottomLabel(band, "brown", pctForFocusLine(basinStart, s), basinStart);
      addFrameBottomLabel(band, "brown", pctForFocusLine(basinEnd, s), basinEnd);
    }}

    if (inspectionStart !== null && inspectionEnd !== null) {{
      addFrameBottomLabel(band, "green", pctForFocusLine(inspectionStart, s), inspectionStart);
      addFrameBottomLabel(band, "green", pctForFocusLine(inspectionEnd, s), inspectionEnd);
    }}

    if (apertureStart !== null && apertureEnd !== null) {{
      const apertureCenter = Math.round((apertureStart + apertureEnd) / 2);
      addFrameBottomLabel(band, "blue", pctForFocusLine(apertureCenter, s), apertureCenter);
    }}
  }}

  const blueCount =
    inspectionStart !== null && inspectionEnd !== null ? (inspectionEnd - inspectionStart + 1) : 0;

  const focusCount =
    apertureStart !== null && apertureEnd !== null ? (apertureEnd - apertureStart + 1) : 0;

  let anchor = 50;

  if (inspectionStart !== null && inspectionEnd !== null) {{
    const center = Math.round((inspectionStart + inspectionEnd) / 2);
    anchor = pctForFocusLine(center, s);
  }}

  summary.innerHTML =
    "<span class='blue'>focus " + focusCount + "</span>" +
    "<span class='green'>blue " + blueCount + "</span>";

  const focusSpan = summary.querySelector(".blue");
  const blueSpan = summary.querySelector(".green");

  if (focusSpan) {{
    focusSpan.style.left = anchor + "%";
    focusSpan.style.transform = "translateX(-50%)";
  }}

  if (blueSpan) {{
    blueSpan.style.left = anchor + "%";
    blueSpan.style.transform = "translateX(-50%)";
  }}
}}

function forceV54G3BSafeSettle() {{
  document.querySelectorAll(".pointLabel, .framePointLabel").forEach(el => {{
    el.style.display = "none";
  }});

  document.querySelectorAll(".inspectionFrame").forEach(frame => {{
    frame.style.setProperty("pointer-events", "auto", "important");
    frame.style.setProperty("z-index", "70", "important");
    frame.style.setProperty("background", "rgba(140,195,230,0.18)", "important");
    frame.style.setProperty("border-left", "6px solid #4f8fbd", "important");
    frame.style.setProperty("border-right", "6px solid #4f8fbd", "important");
    frame.style.setProperty("border-top", "2px solid #4f8fbd", "important");
    frame.style.setProperty("border-bottom", "2px solid #4f8fbd", "important");
  }});

  document.querySelectorAll(".apertureFrame").forEach(frame => {{
    frame.style.setProperty("pointer-events", "none", "important");
    frame.style.setProperty("background", "rgba(247,222,132,0.30)", "important");
    frame.style.setProperty("border-left", "2px solid #d9b43a", "important");
    frame.style.setProperty("border-right", "2px solid #d9b43a", "important");
    frame.style.setProperty("border-top", "1px solid #d9b43a", "important");
    frame.style.setProperty("border-bottom", "1px solid #d9b43a", "important");
  }});

  const saveGreen = document.getElementById("saveGreenCsv");
  if (saveGreen) {{
    saveGreen.textContent = "save blue";
  }}

  renderV54G3BSafeLabels();
}}

/* SECTION 10 — STICKY NOTE */
saveBookmark.addEventListener("click", evt => {{
  const s = state();

  const bookmark = {{
    bookmark_id: "local_" + Date.now(),
    terrain: "Imported_Terrain",
    global_window: s.globalSize,
    focus_window: s.focusSize,
    focus_start: s.start,
    focus_end: s.end,
    focus_width: s.span,

      basin_start: basinStart,
      basin_end: basinEnd,
      inspection_start: inspectionStart,
      inspection_end: inspectionEnd,
          aperture_start: apertureStart,
      aperture_end: apertureEnd,
      selection_mask: JSON.parse(JSON.stringify(selectionMask)),
operator_note: noteText.value,
    unresolved_status: unresolvedText.value,
    next_lawful_revisit: "return under alternate constitution",
    created_local: new Date().toISOString()
  }};

  bookmarkPreview.textContent =
      "card saved"

    bookmark.card_label = "card " + (bookmarks.length + 1);
    bookmarks.push(bookmark);

    const card = document.createElement("div");
    card.style.border = "1px solid #999";
    card.style.padding = "8px";
    card.style.margin = "6px 0";
    card.style.cursor = "pointer";
    card.style.background = "#fafafa";
    card.style.fontFamily = "Consolas, monospace";
    card.style.fontSize = "12px";

    const savedLogCount = countIncludedRowsForBookmark(bookmark);

    card.innerHTML =
      "<div style='display:flex; justify-content:space-between; gap:6px; align-items:center;'>" +
      "<b>" + (bookmark.card_label || ("card " + bookmarks.length)) + "</b>" +
      "<button class='removeBookmarkButton' style='font-size:11px;'>remove</button>" +
      "</div>" +
      "<button class='saveBookmarkCsvButton' style='font-size:11px; margin-top:5px;'>save card to CSV</button><br>" +
      "<button class='addBookmarkToPackButton' style='font-size:11px; margin-top:5px;'>add to pack</button><br>" +
      "saved logs: " + savedLogCount + "<br>" +
      "global: " + bookmark.global_window + "<br>" +
      "focus: " + bookmark.focus_window + "<br>" +
      "basin: " + bookmark.basin_start + "-" + bookmark.basin_end + "<br>" +
      "inspection: " + bookmark.inspection_start + "-" + bookmark.inspection_end + "<br>" +
      
      "aperture: " + bookmark.aperture_start + "-" + bookmark.aperture_end + "<br>" +"note: " + (bookmark.operator_note || "");

    card.querySelector(".removeBookmarkButton").addEventListener("click", evt => {{
      evt.stopPropagation();

      card.remove();

      bookmarks = bookmarks.filter(b => b.bookmark_id !== bookmark.bookmark_id);
      cardPacks.forEach(pack => {{
        pack.cards = pack.cards.filter(b => b.bookmark_id !== bookmark.bookmark_id);
      }});

      renderCardPackSurface();
      bookmarkPreview.textContent = "card removed";
    }});

    card.querySelector(".saveBookmarkCsvButton").addEventListener("click", evt => {{
      evt.stopPropagation();
      saveBookmarkCsvPacket(bookmark);
    }});

    card.querySelector(".addBookmarkToPackButton").addEventListener("click", evt => {{
      evt.stopPropagation();
      addBookmarkToCurrentPack(bookmark);
    }});

    card.addEventListener("click", evt => {{
      const globalIdx = data.sizes.indexOf(parseInt(bookmark.global_window));
      const focusIdx = data.sizes.indexOf(parseInt(bookmark.focus_window));

      if (globalIdx >= 0) globalSizeDial.value = globalIdx;
      if (focusIdx >= 0) focusSizeDial.value = focusIdx;

      spanDial.value = clamp(parseInt(bookmark.focus_width), parseInt(spanDial.min), parseInt(spanDial.max));

      const center = Math.round((parseInt(bookmark.focus_start) + parseInt(bookmark.focus_end)) / 2);
      centerDial.value = clamp(center, 1, data.max_line);

      if (bookmark.basin_start !== null && bookmark.basin_start !== undefined) {{
        basinStart = parseInt(bookmark.basin_start);
        basinEnd = parseInt(bookmark.basin_end);
      }}

      if (bookmark.inspection_start !== null && bookmark.inspection_start !== undefined) {{
        inspectionStart = parseInt(bookmark.inspection_start);
        inspectionEnd = parseInt(bookmark.inspection_end);
      }}

      if (bookmark.selection_mask) {{
        selectionMask = JSON.parse(JSON.stringify(bookmark.selection_mask));
      }} else {{
        resetSelectionMaskForInspection();
      }}

      bookmarkPreview.textContent = "card saved";
      renderInspectionPreviewOnly();
      render();
    }});

    bookmarkCards.appendChild(card);
}});

wireMicroBarPaint();
wireCsvAndSelectionInteraction();
renderCsvPacketSurface();
renderCardPackSurface();
render();
layoutRefineOnce();
setTimeout(() => {{
  forceV54F2Visuals();
  refineNoteCardLayout();
  forceV54GFinalVisuals();
  forceV54G1Tighten();
  forceV54G2ColorShift();
  forceV54G3BSafeSettle();
}}, 0);
setTimeout(() => {{
  renderFocusBottomLabelsAndCounts();
  renderProjectionLines();
  hideOldContextStatusLineSafe();
  forceV54DVisuals();
  forceV54ELayout();
  forceV54F2Visuals();
  refineNoteCardLayout();
}}, 0);
setInterval(forceV54G3BSafeSettle, 500);
</script>
</body>
</html>
"""

html = html.replace("__PAYLOAD__", payload_json)

OUT.write_text(html, encoding="utf-8")
print("WROTE", OUT.resolve())

































