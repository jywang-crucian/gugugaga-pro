from __future__ import annotations

from pathlib import Path

from PIL import Image


def main() -> int:
    logo = Path("resources") / "logo.png"
    icon = Path("resources") / "app.ico"
    if not logo.exists():
        print("logo_not_found")
        return 1
    img = Image.open(logo).convert("RGBA")
    img.save(icon, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print(f"icon_generated:{icon}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
