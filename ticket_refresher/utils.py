import os
import base64
from datetime import datetime
from ticket_refresher.logging_config import logger

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_base64_png(data_uri: str, dir_path: str, prefix: str = "qr") -> str:
    """Salva imagem base64 (data URI) em PNG."""
    ensure_dir(dir_path)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(dir_path, f"{prefix}_{now}.png")
    if data_uri.startswith("data:image"):
        header, b64 = data_uri.split(",", 1)
    else:
        b64 = data_uri
    with open(out, "wb") as f:
        f.write(base64.b64decode(b64))
    logger.info(f"Persistência | sink=arquivo | arquivo={out}")
    return out
