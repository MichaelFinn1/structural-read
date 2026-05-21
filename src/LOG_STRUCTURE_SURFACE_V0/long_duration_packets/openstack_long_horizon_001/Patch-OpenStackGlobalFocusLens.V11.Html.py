from pathlib import Path

base = Path("src/LOG_STRUCTURE_SURFACE_V0/long_duration_packets/openstack_long_horizon_001/visualizations")
src = base / "openstack_global_focus_lens_v10.html"
out = base / "openstack_global_focus_lens_v11.html"

text = src.read_text(encoding="utf-8")
text = text.replace("OpenStack Global Focus Lens V10", "OpenStack Global Focus Lens V11")

inject = r'''
function wheelRangeControl(el, direction) {
  el.addEventListener("wheel", evt => {
    evt.preventDefault();

    const min = parseInt(el.min);
    const max = parseInt(el.max);
    const step = parseInt(el.step || "1");

    let value = parseInt(el.value);
    const delta = evt.deltaY > 0 ? step : -step;

    if (direction === "reverse") {
      value = value - delta;
    } else {
      value = value + delta;
    }

    el.value = clamp(value, min, max);
    render();
  }, { passive: false });
}

wheelRangeControl(globalSizeDial, "normal");
wheelRangeControl(spanDial, "normal");
wheelRangeControl(centerDial, "normal");
wheelRangeControl(focusSizeDial, "normal");
'''

marker = "render();"
idx = text.rfind(marker)
if idx < 0:
    raise RuntimeError("Could not find final render(); marker")

text = text[:idx] + inject + "\n" + text[idx:]

out.write_text(text, encoding="utf-8")
print("WROTE", out)
