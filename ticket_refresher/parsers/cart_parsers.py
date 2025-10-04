from typing import Optional

def get_qr_data_uri(img_ele) -> Optional[str]:
    """Retorna o src base64 do QR Code (data URI)."""
    if not img_ele:
        return None
    src = img_ele.attr("src")
    return (src or None)
