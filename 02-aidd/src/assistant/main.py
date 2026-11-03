import asyncio
import logging
import sys

from assistant.bot import Bot
from assistant.config import Config
from assistant.history import History
from assistant.llm import Llm


def main() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger = logging.getLogger("assistant")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    config = Config()
    history = History()
    llm = Llm(config)
    bot = Bot(config, history, llm)
    logger.info("Бот запущен, модель %s", config.model)
    asyncio.run(bot.run())


if __name__ == "__main__":
    main()
