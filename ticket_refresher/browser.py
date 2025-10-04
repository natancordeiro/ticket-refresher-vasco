from DrissionPage import ChromiumOptions, Chromium
from ticket_refresher.config import AppConfig
from ticket_refresher.logging_config import logger
from ticket_refresher.timing import timed

class BrowserClient:
    """Wrapper do WebPage com configuração centralizada e navegação instrumentada."""

    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.page = self._create_page()

    def _create_page(self) -> WebPage:
        co = ChromiumOptions()

        # Caminho do Chromium no Debian/Ubuntu (ajuste se necessário):
        # em imagens Debian/Ubuntu recentes o binário costuma ser /usr/bin/chromium
        co.set_browser_path('/usr/bin/chromium')

        # Perfil e downloads
        co.set_user_data_path(self.cfg.user_data_dir)
        co.set_download_path(self.cfg.download_dir)

        # Modo headless + flags necessárias para Linux/containers
        co.headless(self.cfg.headless)

        # Flags recomendadas em container Linux para evitar falhas de sandbox e /dev/shm
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-dev-shm-usage')

        browser = Chromium(addr_or_opts=co)
        page = browser.latest_tab
        logger.info("Browser inicializado.")
        return page

    def goto(self, url: str):
        with timed(f"Request iniciado | url={url}"):
            self.page.get(url)
        try:
            html = self.page.html
            logger.debug(f"Request finalizado | url={url} | status=N/A | bytes={len(html)}")
        except Exception:
            logger.debug(f"Request finalizado | url={url} | status=N/A | bytes=?")

    @property
    def current_url(self) -> str:
        return self.page.url

    def screenshot(self, path: str):
        self.page.save_screenshot(path)
        logger.info(f"Persistência | sink=arquivo | arquivo={path}")

    def close(self):
        try:
            self.page.quit()
        finally:
            logger.info("Browser encerrado.")
