import time
from ticket_refresher.logging_config import logger
from ticket_refresher.config import AppConfig

class PaymentService:
    """Orquestra a extração e a persistência de dados do pagamento."""

    def __init__(self, browser, cfg: AppConfig, sink):
        self.page = browser.page
        self.browser = browser
        self.cfg = cfg
        self.sink = sink

    def gentle_wait_after_qr(self):
        # Espera configurável para garantir que a renovação do temporizador do carrinho ocorra
        time.sleep(self.cfg.wait_qr_sleep)
