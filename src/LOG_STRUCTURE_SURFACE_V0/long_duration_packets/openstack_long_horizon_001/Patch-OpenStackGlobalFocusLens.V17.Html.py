from pathlib import Path

path = Path(
    "src/LOG_STRUCTURE_SURFACE_V0/"
    "long_duration_packets/openstack_long_horizon_001/"
    "visualizations/openstack_global_focus_lens_v17.html"
)

text = path.read_text(encoding="utf-8")

text = text.replace(
    "OpenStack Global Focus Lens V16",
    "OpenStack Global Focus Lens V17"
)

text = text.replace(
    "</style>",
    """
.sectionShell {
  border: 2px solid #666;
  margin-top: 18px;
  padding: 12px;
}

.sectionTitle {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
}

.subTitle {
  font-size: 15px;
  margin-bottom: 6px;
  color: #333;
}

.terrainGate {
  border: 2px solid #aa4444;
  padding: 14px;
  margin-bottom: 18px;
  background: #faf7f7;
}

.lensHeader {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.lensLabel {
  font-size: 14px;
  border: 1px solid #777;
  padding: 2px 8px;
  background: #f0f0f0;
}

.projectionGuide {
  height: 40px;
  position: relative;
  margin-top: 2px;
  margin-bottom: 2px;
}

.projectionGuide::before {
  content: "";
  position: absolute;
  left: 25%;
  top: 0;
  width: 1px;
  height: 100%;
  background: red;
  transform: skewX(30deg);
}

.projectionGuide::after {
  content: "";
  position: absolute;
  right: 25%;
  top: 0;
  width: 1px;
  height: 100%;
  background: red;
  transform: skewX(-30deg);
}

.hingeMock {
  margin-top: 10px;
  margin-bottom: 10px;
  font-family: Consolas, monospace;
  white-space: pre;
  color: #444;
}

.workbenchDimmed {
  opacity: 0.35;
  pointer-events: none;
}
</style>
"""
)

insert_top = """
<div class="terrainGate">
  <div class="sectionTitle">
    SECTION 0 — Terrain Admission
  </div>

  <div class="subTitle">
    Declare terrain bounds before descent.
  </div>

  <div style="margin-top:10px;">
    <button id="confirmTerrainBtn">
      Confirm Terrain Admission
    </button>
  </div>
</div>

<div id="workbenchBody" class="workbenchDimmed">
"""

text = text.replace(
    '<div id="wrap">',
    '<div id="wrap">' + insert_top
)

text = text.replace(
    "</body>",
    """
</div>

<script>
const confirmTerrainBtn =
  document.getElementById("confirmTerrainBtn");

const workbenchBody =
  document.getElementById("workbenchBody");

confirmTerrainBtn.addEventListener("click", evt => {
  workbenchBody.classList.remove("workbenchDimmed");
});
</script>

</body>
"""
)

text = text.replace(
    "Global Focus Lens",
    "Dual Lens Workbench"
)

text = text.replace(
    "Global window",
    "Global lens"
)

text = text.replace(
    "Focus window",
    "Focus lens"
)

text = text.replace(
    '<div class="controls">',
    '''
<div class="sectionShell">
<div class="sectionTitle">
SECTION 1 — Dual Lens Projection
</div>

<div class="lensHeader">
  <div class="lensLabel">
    Global Lens ::
  </div>
</div>

<div class="controls">
'''
)

text = text.replace(
    '<div id="focusWrap">',
    '''
<div class="projectionGuide"></div>

<div class="lensHeader">
  <div class="lensLabel">
    Focus Lens ::
  </div>
</div>

<div id="focusWrap">
'''
)

text = text.replace(
    '<div id="linePreviewWrap">',
    '''
<div class="hingeMock">
──────────────
|
|
|
Temporal hinge descent
</div>

<div class="sectionShell">
<div class="sectionTitle">
SECTION 2 — Raw Evidence Descent
</div>

<div id="linePreviewWrap">
'''
)

text = text.replace(
    '<div class="packetTray">',
    '''
</div>

<div class="sectionShell">
<div class="sectionTitle">
SECTION 3 — Preservation / Composition
</div>

<div class="packetTray">
'''
)

text = text.replace(
    '</div>\n</body>',
    '''
</div>
</div>
</body>
'''
)

path.write_text(text, encoding="utf-8")

print("PATCHED", path)
