import time
from contextlib import contextmanager
from ticket_refresher.logging_config import logger

@contextmanager
def timed(msg: str):
    start = time.perf_counter()
    try:
        yield
        elapsed = (time.perf_counter() - start) * 1000
        logger.debug(f"{msg} | tempo_ms={elapsed:.2f}")
    except Exception as e:
        elapsed = (time.perf_counter() - start) * 1000
        logger.error(f"{msg} | erro={type(e).__name__}: {e} | tempo_ms={elapsed:.2f}")
        raise
