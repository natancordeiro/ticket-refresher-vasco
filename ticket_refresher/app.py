import signal
import time

from ticket_refresher.logging_config import logger
from ticket_refresher.config import load_config, AppConfig
from ticket_refresher.browser import BrowserClient
from ticket_refresher.retry import with_retry
from ticket_refresher.services.auth import AuthService
from ticket_refresher.services.cart import CartService
from ticket_refresher.services.payment import PaymentService
from ticket_refresher.persistence.json_sink import JsonSink
from ticket_refresher.timing import timed
from ticket_refresher.exceptions import AutomationError

class App:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.browser = BrowserClient(cfg)
        self.auth = AuthService(self.browser, cfg)
        self.cart = CartService(self.browser, cfg)
        self.sink = JsonSink()
        self.payment = PaymentService(self.browser, cfg, self.sink)
        self._running = True
        signal.signal(signal.SIGINT, self._stop)
        signal.signal(signal.SIGTERM, self._stop)

    def _stop(self, *args):
        self._running = False
        logger.warning("Sinal recebido. Encerrando loop principal...")

    def run_once(self):
        """Executa um ciclo completo: home -> (login se preciso) -> carrinho -> checkout -> QR -> back -> aguardar."""
        with timed("Ciclo | navegação para HOME"):
            self.browser.goto(self.cfg.base_url)

        self.auth.accept_cookies_if_present()

        # Se precisar, efetua login
        if not self.auth.is_logged_in():
            logger.info("Login requerido. Iniciando fluxo de autenticação.")
            login_op = with_retry(self.auth.perform_login, self.cfg, op_name="login")
            login_op()
        else:
            self.auth.log_username_if_present()

        # Ir ao carrinho e iniciar fluxo de pagamento
        with timed("Ciclo | navegação para CARRINHO"):
            self.cart.goto_cart()

        # Execução com retry (elementos às vezes demoram mais)
        checkout_op = with_retry(self.cart.open_checkout_until_qr, self.cfg, op_name="open_checkout_until_qr")
        src = checkout_op()

        # Persistência mínima do QR + pausa curta
        img_ele = self.browser.page.ele('css:img.imply-pay-qrcode', timeout=self.cfg.element_timeout)
        if not img_ele:
            logger.warning("QR encontrado anteriormente, mas não mais presente para persistência de imagem.")

        self.payment.gentle_wait_after_qr()

        # Voltar ao carrinho
        with timed("Ciclo | retorno para CARRINHO"):
            self.cart.back_to_cart()

        # Aguardo longo p/ renovar expiração próximo ciclo
        minutes = self.cfg.renew_wait_minutes
        logger.info(f"Aguardando {minutes} minutos antes do próximo ciclo...")
        time.sleep(minutes * 60)

    def run_forever(self):
        logger.info("Loop principal iniciado. (CTRL+C para parar)")
        try:
            while self._running:
                try:
                    self.run_once()
                except AutomationError as e:
                    logger.error(f"Erro de automação | tipo={type(e).__name__} | mensagem={e}")
                    # screenshot para diagnóstico
                    self.browser.screenshot(f"{self.cfg.screenshot_dir}/error.png")
                    time.sleep(5)
                except Exception as e:
                    logger.critical(f"Erro inesperado | tipo={type(e).__name__} | mensagem={e}")
                    self.browser.screenshot(f"{self.cfg.screenshot_dir}/unexpected.png")
                    time.sleep(5)
        finally:
            self.browser.close()
            logger.info("Loop principal finalizado.")
