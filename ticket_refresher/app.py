import signal
import time

from ticket_refresher.logging_config import logger
from ticket_refresher.config import load_config, AppConfig
from ticket_refresher.browser import BrowserClient
from ticket_refresher.retry import with_retry
from ticket_refresher.services.auth import AuthService
from ticket_refresher.services.cart import CartService
from ticket_refresher.services.payment import PaymentService
from ticket_refresher.services.notifier import TelegramNotifier
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
        self.notifier = TelegramNotifier(cfg)
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

        img_ele = self.browser.page.ele('css:img.imply-pay-qrcode', timeout=self.cfg.element_timeout)
        payload = None
        if img_ele:
            payload = self.payment.capture_and_persist_qr(img_ele)
        else:
            logger.warning("QR encontrado anteriormente, mas não mais presente para persistência de imagem.")

        self.payment.gentle_wait_after_qr()

        with timed("Ciclo | retorno para CARRINHO"):
            self.cart.back_to_cart()

        # >>> ALERTA DE SUCESSO <<<
        try:
            if payload:
                send_ok = with_retry(
                    lambda: self.notifier.alert_success(
                        current_url=payload.get("current_url", ""),
                        qr_file=payload.get("qr_file", ""),
                        next_minutes=self.cfg.renew_wait_minutes,
                    ),
                    self.cfg,
                    op_name="telegram_alert_success",
                )
                send_ok()
        except Exception as _e:
            logger.warning(f"Telegram | falha ao enviar alerta de sucesso | {type(_e).__name__}: {_e}")

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
                    shot = f"{self.cfg.screenshot_dir}/error.png"
                    self.browser.screenshot(shot)
                    try:
                        send_err = with_retry(
                            lambda: self.notifier.alert_error(type(e).__name__, str(e), screenshot_path=shot),
                            self.cfg,
                            op_name="telegram_alert_error",
                        )
                        send_err()
                    except Exception as _e:
                        logger.warning(f"Telegram | falha ao enviar alerta de erro | {type(_e).__name__}: {_e}")
                    time.sleep(5)

                except Exception as e:
                    logger.critical(f"Erro inesperado | tipo={type(e).__name__} | mensagem={e}")
                    shot = f"{self.cfg.screenshot_dir}/unexpected.png"
                    self.browser.screenshot(shot)
                    try:
                        send_err = with_retry(
                            lambda: self.notifier.alert_error(type(e).__name__, str(e), screenshot_path=shot),
                            self.cfg,
                            op_name="telegram_alert_error",
                        )
                        send_err()
                    except Exception as _e:
                        logger.warning(f"Telegram | falha ao enviar alerta de erro | {type(_e).__name__}: {_e}")
                    time.sleep(5)
        finally:
            self.browser.close()
            logger.info("Loop principal finalizado.")
