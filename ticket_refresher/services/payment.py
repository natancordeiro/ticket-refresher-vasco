import time
from typing import Dict, Any
from ticket_refresher.logging_config import logger
from ticket_refresher.config import AppConfig
from ticket_refresher.parsers.cart_parsers import get_qr_data_uri
from ticket_refresher.exceptions import PaymentFlowError
from ticket_refresher.utils import save_base64_png

class PaymentService:
    """Orquestra a extração e a persistência de dados do pagamento."""

    def __init__(self, browser, cfg: AppConfig, sink):
        self.page = browser.page
        self.browser = browser
        self.cfg = cfg
        self.sink = sink

    def capture_and_persist_qr(self, img_ele) -> Dict[str, Any]:
        data_uri = get_qr_data_uri(img_ele)
        if not data_uri:
            raise PaymentFlowError("Falha ao extrair data URI do QR.")
        qr_path = save_base64_png(data_uri, self.cfg.screenshot_dir, prefix="qr")
        payload = {
            "current_url": self.browser.current_url,
            "qr_file": qr_path,
        }
        self.sink.persist(payload)
        return payload

    def gentle_wait_after_qr(self):
        # Espera configurável para garantir que a renovação do temporizador do carrinho ocorra
        time.sleep(self.cfg.wait_qr_sleep)
