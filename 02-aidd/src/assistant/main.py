import asyncio

from assistant.bot import Bot
from assistant.config import Config
from assistant.history import History
from assistant.llm import Llm


def main() -> None:
    config = Config()
    history = History()
    llm = Llm(config)
    bot = Bot(config, history, llm)
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
