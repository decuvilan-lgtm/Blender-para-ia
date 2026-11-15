"""Capture the current virtual X11 desktop as a PNG."""
from pathlib import Path
import os
import sys

import mss
from PIL import Image

output = Path(sys.argv[1] if len(sys.argv) > 1 else "artifacts/desktop.png")
output.parent.mkdir(parents=True, exist_ok=True)
with mss.mss() as capture:
    shot = capture.grab(capture.monitors[0])
    image = Image.frombytes("RGB", shot.size, shot.rgb)
    image.save(output)
print(output)
