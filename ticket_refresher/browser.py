from DrissionPage import ChromiumOptions, WebPage
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
        co.auto_port()
        co.headless(self.cfg.headless)
        # co.set_user_data_path(self.cfg.user_data_dir)
        co.set_download_path(self.cfg.download_dir)
        page = WebPage(chromium_options=co, timeout=self.cfg.navigation_timeout)
        logger.info("Browser inicializado.")
        return page

    def goto(self, url: str):
        with timed(f"Request iniciado | url={url}"):
            self.page.get(url)
        # Tentar obter html length p/ 'bytes'
        try:
            html = self.page.html
            logger.debug(f"Request finalizado | url={url} | status=N/A | bytes={len(html)}")
        except Exception:
            logger.debug(f"Request finalizado | url={url} | status=N/A | bytes=?")

    @property
    def current_url(self) -> str:
        return self.page.url

    def screenshot(self, path: str):
        self.page.get_screenshot(path)
        logger.info(f"Persistência | sink=arquivo | arquivo={path}")

    def close(self):
        try:
            self.page.quit()
        finally:
            logger.info("Browser encerrado.")
