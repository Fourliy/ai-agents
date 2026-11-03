class History:
    def __init__(self) -> None:
        self._chats: dict[int, list[dict[str, str]]] = {}

    def add(self, chat_id: int, role: str, content: str) -> None:
        messages = self._chats.setdefault(chat_id, [])
        messages.append({"role": role, "content": content})
        del messages[:-20]

    def messages(self, chat_id: int) -> list[dict[str, str]]:
        return self._chats.get(chat_id, [])
