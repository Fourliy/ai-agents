import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    def __init__(self) -> None:
        load_dotenv(Path(__file__).resolve().parents[2] / ".env")
        self.token = self._required("TELEGRAM_BOT_TOKEN")
        self.api_key = self._required("OPENROUTER_API_KEY")
        self.model = self._required("OPENROUTER_MODEL")
        self.system_prompt = self._required("SYSTEM_PROMPT")

    def _required(self, name: str) -> str:
        value = os.environ.get(name, "").strip()
        if not value:
            logger.info("Не задана переменная %s", name)
            raise SystemExit(f"Не задана переменная {name}")
        return value
