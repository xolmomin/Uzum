import base64
import io

import qrcode


def _generate_qr_image_base64(payload: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return qr_base64


def _status_cache_key(user_id: int) -> str:
    return f"consumers:user_status:{user_id}"
