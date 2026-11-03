from aiogram import Bot as TelegramBot
from aiogram import Dispatcher
from aiogram import F
from aiogram.types import Message

from assistant.config import Config
from assistant.history import History
from assistant.llm import Llm


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
        self._history.add(chat_id, "user", message.text or "")
        try:
            answer = await self._llm.complete(self._history.messages(chat_id))
        except Exception:
            await message.answer("Не удалось получить ответ.")
            return
        if not answer.strip():
            await message.answer("Не удалось получить ответ.")
            return
        self._history.add(chat_id, "assistant", answer)
        await message.answer(answer)

    async def _on_other(self, message: Message) -> None:
        await message.answer("Принимаю только текст.")
