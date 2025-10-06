import os, html
import requests
from ticket_refresher.logging_config import logger
from ticket_refresher.config import AppConfig

class TelegramNotifier:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.enabled = bool(cfg.telegram_enabled and cfg.telegram_bot_token and cfg.telegram_chat_id)
        if not self.enabled:
            logger.info("Telegram | desativado (variáveis ausentes ou TELEGRAM_ENABLED=false).")

    def _send(self, text: str):
        if not self.enabled:
            return
        url = f"https://api.telegram.org/bot{self.cfg.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.cfg.telegram_chat_id,
            "text": text,
            "parse_mode": self.cfg.telegram_parse_mode,
            "disable_web_page_preview": True,
        }
        logger.info(f"Request iniciado | url=Telegram.sendMessage | tentativa 1/1")
        resp = requests.post(url, json=payload, timeout=10)
        size = len(resp.text or "")
        logger.debug(f"Request finalizado | url=Telegram.sendMessage | status={resp.status_code} | bytes={size}")
        if not resp.ok:
            raise RuntimeError(f"Telegram API falhou. status={resp.status_code} body={resp.text[:200]}")

    def alert_success(self, current_url: str, qr_file: str, next_minutes: int):
        txt = (
            "✅ <b>Carrinho renovado com sucesso</b>\n"
            f"URL: <code>{html.escape(current_url)}</code>\n"
            f"QR salvo: <code>{html.escape(os.path.basename(qr_file))}</code>\n"
            f"Próximo ciclo em ~{next_minutes} min."
        )
        self._send(txt)

    def alert_error(self, err_type: str, err_msg: str, screenshot_path: str | None = None):
        extra = f"\nScreenshot: <code>{html.escape(screenshot_path)}</code>" if screenshot_path else ""
        txt = (
            "❌ <b>Erro ao renovar carrinho</b>\n"
            f"Tipo: <code>{html.escape(err_type)}</code>\n"
            f"Msg: <code>{html.escape(err_msg)[:4000]}</code>{extra}"
        )
        self._send(txt)
