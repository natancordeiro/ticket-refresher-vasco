import random
import time
from typing import Callable, Any
from ticket_refresher.logging_config import logger
from ticket_refresher.config import AppConfig

def with_retry(fn: Callable[..., Any], cfg: AppConfig, op_name: str):
    """Executa função com retry exponencial + jitter opcional."""
    attempts = cfg.retry.max_attempts
    base = cfg.retry.backoff_base
    jitter = cfg.retry.jitter

    def _call(*args, **kwargs):
        for i in range(1, attempts + 1):
            try:
                logger.debug(f"Retry | op={op_name} | tentativa={i}/{attempts}")
                return fn(*args, **kwargs)
            except Exception as e:
                if i == attempts:
                    logger.error(f"Retry esgotado | op={op_name} | erro={type(e).__name__}: {e}")
                    raise
                sleep_s = (base ** (i - 1))
                if jitter:
                    sleep_s += random.uniform(0, 0.5)
                logger.warning(f"Retry | op={op_name} | tentativa={i}/{attempts} | backoff={sleep_s:.2f}s | erro={type(e).__name__}: {e}")
                time.sleep(sleep_s)
    return _call
