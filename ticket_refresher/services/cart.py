import time
from ticket_refresher.logging_config import logger
from ticket_refresher.config import AppConfig
from ticket_refresher.exceptions import ElementNotFoundError, PaymentFlowError
from ticket_refresher.timing import timed

class CartService:
    """Navegação e ações no carrinho."""

    SEL_CONTINUAR_CHECKOUT = (
        'xpath://button[@ng-click="finalizarReserva(reserva)" and not(@disabled)]'
    )
    SEL_SEGUIR_PAGAMENTO = (
        'xpath://button[@id="imply-pay-neo-payment" and not(@disabled)]'
    )
    SEL_QR_IMG = 'css:img.imply-pay-qrcode'

    def __init__(self, browser, cfg: AppConfig):
        self.page = browser.page
        self.browser = browser
        self.cfg = cfg

    def goto_cart(self):
        self.browser.goto(self.cfg.cart_url)
        time.sleep(2)

    def open_checkout_until_qr(self) -> str:
        """Clica em 'CONTINUAR PARA CHECKOUT...' e depois 'Seguir para o pagamento' e espera QR."""
        with timed("Checkout | continuar para checkout seguro"):
            btn = self.page.ele(self.SEL_CONTINUAR_CHECKOUT, timeout=self.cfg.element_timeout)
            if not btn:
                raise ElementNotFoundError("Botão 'CONTINUAR PARA CHECKOUT SEGURO' não encontrado.")
            btn.click()

        time.sleep(3)

        with timed("Checkout | seguir para pagamento"):
            btn2 = self.page.ele(self.SEL_SEGUIR_PAGAMENTO, timeout=self.cfg.element_timeout)
            if not btn2:
                raise ElementNotFoundError("Botão 'Seguir para o pagamento' não encontrado.")
            time.sleep(1)
            btn2.click()

        time.sleep(3)

        # Aguardar QR
        with timed("Pagamento | aguardando QR"):
            qr = self.page.ele(self.SEL_QR_IMG, timeout=self.cfg.element_timeout)
            if not qr:
                raise PaymentFlowError("QR Code não apareceu.")
            src = qr.attr("src")
            if not src:
                raise PaymentFlowError("QR Code sem atributo 'src'.")
            logger.info("Parsing finalizado | itens_extraídos=1 | página=checkout")
            return src

    def back_to_cart(self):
        self.browser.goto(self.cfg.cart_url)
        time.sleep(2)
