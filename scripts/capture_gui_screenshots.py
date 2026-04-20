from __future__ import annotations

from pathlib import Path
import time
import sys

from PIL import ImageGrab

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gui.app import USBForensicsApp


def capture_window(app: USBForensicsApp, out_path: Path) -> None:
    app.update_idletasks()
    app.update()
    x = app.winfo_rootx()
    y = app.winfo_rooty()
    w = app.winfo_width()
    h = app.winfo_height()
    if w <= 0 or h <= 0:
        raise RuntimeError("Application window has invalid dimensions for screenshot capture")

    # Small pause ensures widgets are painted before capture.
    time.sleep(0.6)
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(out_path)


def main() -> None:
    shots_dir = PROJECT_ROOT / "report and paper" / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    app = USBForensicsApp()

    # Give Tk time to fully render the first page.
    app.after(1200, lambda: capture_window(app, shots_dir / "01_devices_page.png"))
    app.after(2500, lambda: app.show_page("analysis"))
    app.after(3600, lambda: capture_window(app, shots_dir / "02_analysis_page.png"))
    app.after(4700, lambda: app.show_page("export"))
    app.after(5800, lambda: capture_window(app, shots_dir / "03_export_page.png"))
    app.after(7000, app.destroy)

    app.mainloop()


if __name__ == "__main__":
    main()
