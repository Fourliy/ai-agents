import asyncio

from assistant.bot import Bot
from assistant.config import Config
from assistant.llm import Llm


def main() -> None:
    config = Config()
    llm = Llm(config)
    bot = Bot(config, llm)
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
