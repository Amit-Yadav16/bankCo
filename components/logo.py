import base64
from pathlib import Path
from functools import lru_cache

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

@lru_cache(maxsize=4)
def get_logo_b64(icon_only: bool = False) -> str:
    """Return base64 data URI of the user-provided BankCo logo."""
    filename = "logo_icon.png" if icon_only else "logo.png"
    filepath = ASSETS_DIR / filename
    if not filepath.exists():
        filepath = ASSETS_DIR / "logo.jpg"
    
    if filepath.exists():
        data = filepath.read_bytes()
        ext = filepath.suffix.lstrip(".").lower()
        mime = f"image/{ext if ext != 'jpg' else 'jpeg'}"
        return f"data:{mime};base64,{base64.b64encode(data).decode('utf-8')}"
    return ""

def render_logo_img(height: int = 34, icon_only: bool = True, extra_style: str = "") -> str:
    """Return an <img> tag for the BankCo logo."""
    b64 = get_logo_b64(icon_only=icon_only)
    if b64:
        return f'<img src="{b64}" alt="BankCo Logo" style="height:{height}px; width:auto; vertical-align:middle; object-fit:contain; {extra_style}" />'
    return ""
