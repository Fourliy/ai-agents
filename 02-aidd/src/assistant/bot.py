import logging

from aiogram import Bot as TelegramBot
from aiogram import Dispatcher
from aiogram import F
from aiogram.types import Message

from assistant.config import Config
from assistant.history import History
from assistant.llm import Llm

logger = logging.getLogger(__name__)

_TELEGRAM_LIMIT = 4096


def _parts(text: str) -> list[str]:
    parts: list[str] = []
    rest = text
    while rest:
        if len(rest) <= _TELEGRAM_LIMIT:
            parts.append(rest)
            break
        cut = rest.rfind("\n", 0, _TELEGRAM_LIMIT)
        if cut <= 0:
            cut = _TELEGRAM_LIMIT
        parts.append(rest[:cut])
        rest = rest[cut:].lstrip("\n")
    return parts


class Bot:
    def __init__(self, config: Config, history: History, llm: Llm) -> None:
        self._history = history
        self._llm = llm
        self._telegram = TelegramBot(token=config.token)
        self._dispatcher = Dispatcher()
        self._dispatcher.message.register(self._on_text, F.text)
        self._dispatcher.message.register(self._on_other)

    async def run(self) -> None:
        await self._dispatcher.start_polling(self._telegram)

    async def _on_text(self, message: Message) -> None:
        chat_id = message.chat.id
        logger.info("Чат %s", chat_id)
        self._history.add(chat_id, "user", message.text or "")
        try:
            answer = await self._llm.complete(self._history.messages(chat_id))
        except Exception as exc:
            logger.info("Чат %s, %s", chat_id, exc)
            await message.answer("Не удалось получить ответ.")
            return
        if not answer.strip():
            logger.info("Чат %s, пустой ответ", chat_id)
            await message.answer("Не удалось получить ответ.")
            return
        self._history.add(chat_id, "assistant", answer)
        for part in _parts(answer):
            await message.answer(part)

    async def _on_other(self, message: Message) -> None:
        logger.info("Чат %s, сообщение пропущено", message.chat.id)
        await message.answer("Принимаю только текст.")
