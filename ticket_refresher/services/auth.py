import time
from ticket_refresher.logging_config import logger
from ticket_refresher.config import AppConfig
from ticket_refresher.exceptions import LoginFailedError, ElementNotFoundError
from ticket_refresher.timing import timed

class AuthService:
    """Responsável por login e verificação de sessão."""

    # Selectors
    SEL_COOKIES_BTN = 'xpath://button[contains(@class,"button-accept-cookie")]'
    SEL_LOGIN_ANCHOR = 'xpath://a[@ng-click="login(true,null)" and not(@ng-show="User")]'
    SEL_PUBLICO_GERAL_LINK = 'xpath://a[.//p[contains(text(),"Público Geral - Jogos")]]'
    SEL_INPUT_EMAIL = 'xpath://input[@type="email" and @name="_username"]'
    SEL_INPUT_PASSWORD = 'xpath://input[@name="_password"]'
    SEL_BTN_LOGIN = 'xpath://button[.//span[normalize-space()="Login"]]'
    SEL_USER_ANCHOR = 'xpath://span[@ng-if="User.dsctipo"]'

    FACIAL_URL = "https://vasco.eleventickets.com/FacialRecognition"
    HOME_FRAGMENT = "https://vasco.eleventickets.com/#!/home"

    def __init__(self, browser, cfg: AppConfig):
        self.page = browser.page
        self.browser = browser
        self.cfg = cfg

    def accept_cookies_if_present(self):
        """Clica no botão 'ACEITAR TODOS OS COOKIES' se estiver visível."""
        btn = self.page.ele(self.SEL_COOKIES_BTN, timeout=2)
        if btn:
            btn.click()
            from time import sleep
            sleep(0.5)
            logger.info("Cookies | ACEITAR TODOS OS COOKIES clicado.")

    def is_logged_in(self) -> bool:
        anchor = self.page.ele(self.SEL_USER_ANCHOR, timeout=1)
        if anchor:
            return anchor
        else:
            return False

    def log_username_if_present(self):
        anchor = self.page.ele(self.SEL_USER_ANCHOR, timeout=1)
        username = anchor.parent().text.strip() if anchor else None
        if username:
            logger.info(f"Login verificado | usuário='{username}'")
        else:
            logger.warning("Login | anchor de usuário encontrado, mas não foi possível extrair o nome.")

    def perform_login(self):
        with timed("Login | início"):
            # Abrir modal de login
            login_anchor = self.page.ele(self.SEL_LOGIN_ANCHOR, timeout=self.cfg.element_timeout)
            if not login_anchor:
                if self.is_logged_in():
                    logger.info("Login | já logado, pulando.")
                    return
                raise ElementNotFoundError("Botão de login não encontrado.")
            login_anchor.click()
            time.sleep(1)

            # Escolher 'Público Geral - Jogos'
            publico = self.page.ele(self.SEL_PUBLICO_GERAL_LINK, timeout=self.cfg.element_timeout)
            if not publico:
                raise ElementNotFoundError("Link 'Público Geral - Jogos' não encontrado.")
            publico.click()
            time.sleep(1)

            # Preencher credenciais
            email = self.page.ele(self.SEL_INPUT_EMAIL, timeout=self.cfg.element_timeout)
            pwd = self.page.ele(self.SEL_INPUT_PASSWORD, timeout=self.cfg.element_timeout)
            if not email or not pwd:
                raise ElementNotFoundError("Inputs de email/senha não encontrados.")

            email.clear()
            email.input(self.cfg.login_email)
            pwd.clear()
            pwd.input(self.cfg.login_password)

            # Clicar em Login
            btn = self.page.ele(self.SEL_BTN_LOGIN, timeout=self.cfg.element_timeout)
            if not btn:
                raise ElementNotFoundError("Botão 'Login' não encontrado.")
            btn.click()

        # Verificar redirecionamento esperado
        with timed("Login | verificação de redirecionamento"):
            time.sleep(2)
            cur = self.browser.current_url
            if (self.FACIAL_URL in cur) or (self.HOME_FRAGMENT in cur):
                logger.info(f"Login | redirecionado para '{cur}' (OK)")
            else:
                # Tenta ir ao HOME manualmente
                logger.warning(f"Login | redirecionamento inesperado: '{cur}' | tentando HOME")
                self.browser.goto(self.cfg.base_url)
                time.sleep(1)

        time.sleep(5)
        self.browser.goto(self.cfg.cart_url)

        # Checagem final
        time.sleep(3)
        if not self.is_logged_in():
            # Screenshot para diagnóstico
            self.browser.screenshot(f"{self.cfg.screenshot_dir}/login_failed.png")
            raise LoginFailedError("Login não foi validado pelo marcador 'User'.")

        self.log_username_if_present()
        logger.info("Login | finalizado com sucesso.")
