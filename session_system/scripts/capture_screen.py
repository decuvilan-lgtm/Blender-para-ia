"""Capture and validate the current virtual X11 desktop as a PNG.

A black/empty desktop is a failed visual test, not a successful artifact.
"""
from pathlib import Path
import sys

import mss
from PIL import Image, ImageStat

output = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/desktop.png")
output.parent.mkdir(parents=True, exist_ok=True)

with mss.mss() as capture:
    if len(capture.monitors) < 2:
        raise RuntimeError("No X11 monitor was reported by mss.")
    shot = capture.grab(capture.monitors[0])
    image = Image.frombytes("RGB", shot.size, shot.rgb)
    image.save(output)

stats = ImageStat.Stat(image)
mean = sum(stats.mean) / 3
stddev = sum(stats.stddev) / 3
bbox = image.getbbox()
print(f"Captured {output} ({image.width}x{image.height}); mean={mean:.2f}; stddev={stddev:.2f}; bbox={bbox}")

# A GUI desktop should not be uniformly black. This catches the known failure.
if bbox is None or mean < 2.0 or stddev < 1.0:
    raise SystemExit("VISUAL VALIDATION FAILED: captured desktop is empty or effectively black.")
