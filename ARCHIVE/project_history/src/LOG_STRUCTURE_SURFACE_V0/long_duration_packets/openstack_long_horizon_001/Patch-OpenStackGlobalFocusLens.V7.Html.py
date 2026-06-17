from pathlib import Path
import re

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v6.html"
out = base / "openstack_global_focus_lens_v7.html"

text = src.read_text(encoding="utf-8")

text = text.replace("OpenStack Global Focus Lens V6", "OpenStack Global Focus Lens V7")

text = text.replace("</style>", """
.bottomGrid { display: grid; grid-template-columns: 1fr 360px; gap: 16px; align-items: start; }
.cardTray { border: 1px solid #999; padding: 10px; max-height: 320px; overflow: auto; }
.card { border: 1px solid #777; padding: 8px; margin: 8px 0; cursor: pointer; background: #fafafa; }
.cardTitle { font-weight: bold; }
.cardMeta { font-size: 12px; color: #333; margin-top: 4px; }
.deleteBtn { float: right; }
</style>""")

text = re.sub(
    r'<div class="box">\s*<div>Investigatory sticky note</div>[\s\S]*?<pre id="bookmarkPreview"[\s\S]*?</pre>\s*</div>',
    '''
<div class="bottomGrid">
  <div class="box">
    <div>Investigatory sticky note</div>
    <input id="noteText" type="text" placeholder="Why is this region interesting?" style="width:100%; font-size:16px; padding:6px;">
    <input id="unresolvedText" type="text" placeholder="What remains unresolved?" style="width:100%; font-size:16px; padding:6px; margin-top:8px;">
    <button id="saveBookmark" style="margin-top:10px; font-size:16px;">Save sticky note</button>
    <pre id="bookmarkPreview" style="border:1px solid #999; padding:10px; white-space:pre-wrap; font-family:Consolas, monospace; font-size:13px;"></pre>
  </div>

  <div class="cardTray">
    <div style="font-size:18px; text-align:center;">Saved sticky notes</div>
    <div id="cards"></div>
  </div>
</div>
''',
    text,
    count=1
)

text = text.replace(
'const bookmarkPreview = document.getElementById("bookmarkPreview");',
'''const bookmarkPreview = document.getElementById("bookmarkPreview");
const cards = document.getElementById("cards");
let bookmarks = [];'''
)

text = re.sub(
    r'saveBookmark\.addEventListener\("click", evt => \{[\s\S]*?\n\}\);',
    r'''function renderCards() {
  cards.innerHTML = "";

  bookmarks.forEach((b, idx) => {
    const card = document.createElement("div");
    card.className = "card";

    const del = document.createElement("button");
    del.className = "deleteBtn";
    del.textContent = "x";
    del.addEventListener("click", evt => {
      evt.stopPropagation();
      bookmarks.splice(idx, 1);
      renderCards();
    });

    const title = document.createElement("div");
    title.className = "cardTitle";
    const prefix = b.operator_note ? b.operator_note.substring(0, 28) : "untitled";
    title.textContent = prefix + " | " + b.focus_start + "-" + b.focus_end;

    const meta = document.createElement("div");
    meta.className = "cardMeta";
    meta.textContent = "g" + b.global_window + " f" + b.focus_window + " raw " + b.raw_start + "-" + b.raw_end;

    card.appendChild(del);
    card.appendChild(title);
    card.appendChild(meta);

    card.addEventListener("click", evt => {
      const gi = data.sizes.indexOf(parseInt(b.global_window));
      const fi = data.sizes.indexOf(parseInt(b.focus_window));

      if (gi >= 0) globalSizeDial.value = gi;
      if (fi >= 0) focusSizeDial.value = fi;

      spanDial.value = b.focus_width;
      centerDial.value = Math.round((parseInt(b.focus_start) + parseInt(b.focus_end)) / 2);

      noteText.value = b.operator_note;
      unresolvedText.value = b.unresolved_status;

      render();
      previewLineRange(parseInt(b.raw_start), parseInt(b.raw_end));
    });

    cards.appendChild(card);
  });
}

saveBookmark.addEventListener("click", evt => {
  const s = state();

  const bookmark = {
    bookmark_id: "local_" + Date.now(),
    terrain: "OpenStack_long_normal2",
    global_window: s.globalSize,
    focus_window: s.focusSize,
    focus_start: s.start,
    focus_end: s.end,
    focus_width: s.span,
    raw_start: s.start,
    raw_end: s.end,
    operator_note: noteText.value,
    unresolved_status: unresolvedText.value,
    next_lawful_revisit: "return under alternate constitution",
    created_local: new Date().toISOString()
  };

  bookmarks.push(bookmark);
  renderCards();

  bookmarkPreview.textContent =
    "Saved sticky note to tray.\\n\\n" + JSON.stringify(bookmark, null, 2);

  noteText.value = "";
  unresolvedText.value = "";
});''',
    text,
    count=1
)

text = text.replace(
'''globalBar.addEventListener("wheel", evt => {
  evt.preventDefault();

  let idx = parseInt(focusSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  focusSizeDial.value = clamp(idx, parseInt(focusSizeDial.min), parseInt(focusSizeDial.max));
  render();
});''',
'''globalBar.addEventListener("wheel", evt => {
  evt.preventDefault();

  let idx = parseInt(globalSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  globalSizeDial.value = clamp(idx, parseInt(globalSizeDial.min), parseInt(globalSizeDial.max));
  render();
});

focusBar.addEventListener("wheel", evt => {
  evt.preventDefault();

  let idx = parseInt(focusSizeDial.value);
  idx = evt.deltaY > 0 ? idx + 1 : idx - 1;

  focusSizeDial.value = clamp(idx, parseInt(focusSizeDial.min), parseInt(focusSizeDial.max));
  render();
});'''
)

out.write_text(text, encoding="utf-8")
print("WROTE", out)
