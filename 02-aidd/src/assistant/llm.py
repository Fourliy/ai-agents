from openai import AsyncOpenAI

from assistant.config import Config


class Llm:
    def __init__(self, config: Config) -> None:
        self._model = config.model
        self._prompt = config.system_prompt
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=60,
        )

    async def complete(self, messages: list[dict[str, str]]) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "system", "content": self._prompt}, *messages],
        )
        return response.choices[0].message.content or ""
