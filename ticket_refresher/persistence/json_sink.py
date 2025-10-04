import json, os
from datetime import datetime
from typing import Dict, Any
from ticket_refresher.persistence.sink import Sink
from ticket_refresher.logging_config import logger

class JsonSink(Sink):
    def __init__(self, folder: str = "runs"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def persist(self, payload: Dict[str, Any]) -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.folder, f"session_{ts}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        logger.info(f"Persistência | sink=arquivo | arquivo={path} | contagem={len(payload)}")
