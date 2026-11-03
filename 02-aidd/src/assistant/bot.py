from aiogram import Bot as TelegramBot
from aiogram import Dispatcher
from aiogram import F
from aiogram.types import Message

from assistant.config import Config
from assistant.llm import Llm


class Bot:
    def __init__(self, config: Config, llm: Llm) -> None:
        self._llm = llm
        self._telegram = TelegramBot(token=config.token)
        self._dispatcher = Dispatcher()
        self._dispatcher.message.register(self._on_text, F.text)

    async def run(self) -> None:
        await self._dispatcher.start_polling(self._telegram)

    async def _on_text(self, message: Message) -> None:
        answer = await self._llm.complete(message.text or "")
        await message.answer(answer)
