#!/usr/bin/env python3
"""
CLI бот для взаимодействия с LLM через OpenRouter.
Демонстрирует работу с историей диалога, метриками и красивым выводом.
"""

import os
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import box


# Инициализация Rich консоли для красивого вывода
console = Console()

# Системный промпт - определяет роль и поведение ассистента
# ЗАДАНИЕ: Вставьте сюда ваш системный промпт, который определит поведение бота
# Например: "Ты — профессиональный банковский консультант..."
SYSTEM_PROMPT = "Ты специалист - нутрицолог. Ты помогаешь с питанием и спортом, помогаешь с выбором продуктов и упражнений. Помогаешь людям быть лучше без жестких диет и неадекватных тренировок. Общайся непринудительно, как с другом, будь мотиватором для человека, ведь он будет проходить тяжелый путь."

# Стратегия 3: системный промпт всегда, плюс начало диалога и хвост.
# Системный промпт в эти числа не входит.
# Один обмен — это два сообщения: реплика пользователя и ответ бота.
PINNED_HEAD_MESSAGES = 3
MAX_HISTORY_MESSAGES = 10


class ChatBot:
    """Простой CLI бот для общения с LLM."""

    def __init__(self):
        """Инициализация бота с загрузкой конфигурации."""
        load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.model_name = os.getenv("MODEL_NAME", "openai/gpt-4o-mini:free")

        if not api_key:
            console.print("[red]❌ Ошибка: OPENROUTER_API_KEY не найден в .env файле![/red]")
            sys.exit(1)

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

        self.conversation_history: List[Dict[str, str]] = []

        if SYSTEM_PROMPT:
            self.conversation_history.append({
                "role": "system",
                "content": SYSTEM_PROMPT
            })

        self.session_metrics = {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "messages_count": 0,
        }

    def add_message(self, role: str, content: str):
        """Добавить сообщение в историю диалога.

        Стратегия 3: системный промпт хранится всегда. Из диалога остаются
        первые PINNED_HEAD_MESSAGES реплик и последние MAX_HISTORY_MESSAGES.
        Середина между ними отбрасывается. Пока реплик меньше, чем сумма
        этих двух лимитов, история не режется.
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })

        # Системный промпт — первое сообщение и в лимит не входит.
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            system_messages = self.conversation_history[:1]
            dialogue_messages = self.conversation_history[1:]
        else:
            system_messages = []
            dialogue_messages = self.conversation_history

        history_limit = PINNED_HEAD_MESSAGES + MAX_HISTORY_MESSAGES
        if len(dialogue_messages) > history_limit:
            head = dialogue_messages[:PINNED_HEAD_MESSAGES]
            tail = dialogue_messages[-MAX_HISTORY_MESSAGES:]
            dialogue_messages = head + tail

        self.conversation_history = system_messages + dialogue_messages

    def clear_history(self):
        """Очистить историю диалога."""
        self.conversation_history = []
        if SYSTEM_PROMPT:
            self.conversation_history.append({
                "role": "system",
                "content": SYSTEM_PROMPT
            })
        console.print("[yellow]📝 История диалога очищена[/yellow]\n")

    def display_metrics(self, usage: Optional[dict], finish_reason: Optional[str] = None):
        """Отобразить метрики и метаданные ответа."""
        if not usage:
            return

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        self.session_metrics["total_prompt_tokens"] += prompt_tokens
        self.session_metrics["total_completion_tokens"] += completion_tokens
        self.session_metrics["total_tokens"] += total_tokens
        self.session_metrics["messages_count"] += 1

        table = Table(title="📊 Метрики ответа", box=box.ROUNDED, show_header=True)
        table.add_column("Параметр", style="cyan")
        table.add_column("Значение", style="green")

        table.add_row("Модель", self.model_name)
        table.add_row("Prompt токены", str(prompt_tokens))
        table.add_row("Completion токены", str(completion_tokens))
        table.add_row("Всего токены", str(total_tokens))

        if finish_reason:
            table.add_row("Finish reason", finish_reason)

        console.print(table)

        session_table = Table(title="🎯 Статистика сессии", box=box.ROUNDED)
        session_table.add_column("Параметр", style="cyan")
        session_table.add_column("Значение", style="magenta")

        session_table.add_row("Сообщений", str(self.session_metrics["messages_count"]))
        session_table.add_row("Всего токенов", str(self.session_metrics["total_tokens"]))

        console.print(session_table)
        console.print()

    def display_stats(self):
        """Показать статистику сессии."""
        console.print("\n[bold cyan]📈 Статистика текущей сессии:[/bold cyan]")

        stats_table = Table(box=box.DOUBLE)
        stats_table.add_column("Метрика", style="cyan", no_wrap=True)
        stats_table.add_column("Значение", style="green")

        stats_table.add_row("Модель", self.model_name)
        stats_table.add_row("Сообщений в сессии", str(self.session_metrics["messages_count"]))
        stats_table.add_row("Сообщений в истории", str(len(self.conversation_history)))
        stats_table.add_row("Prompt токены", str(self.session_metrics["total_prompt_tokens"]))
        stats_table.add_row("Completion токены", str(self.session_metrics["total_completion_tokens"]))
        stats_table.add_row("Всего токены", str(self.session_metrics["total_tokens"]))

        console.print(stats_table)
        console.print()

    def send_message(self, user_message: str) -> Optional[str]:
        """Отправить сообщение в LLM и получить ответ."""
        self.add_message("user", user_message)

        try:
            with console.status("[bold green]🤔 Думаю...", spinner="dots"):
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=self.conversation_history,
                    max_tokens=200,
                    # Иначе модель тратит max_tokens на скрытые рассуждения
                    # и возвращает пустой content с finish_reason=length.
                    extra_body={"reasoning": {"enabled": False}},
                )

            assistant_message = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason

            if not isinstance(assistant_message, str) or not assistant_message.strip():
                console.print(
                    "[red]Модель вернула пустой текст. "
                    f"Finish reason: {finish_reason or 'не указан'}. "
                    "Реплика в историю не записана.[/red]\n"
                )
                if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                    self.conversation_history.pop()
                return None

            self.add_message("assistant", assistant_message)

            console.print(Panel(
                Markdown(assistant_message),
                title="🤖 Ассистент",
                border_style="blue",
                padding=(1, 2)
            ))

            self.display_metrics(response.usage.model_dump() if response.usage else None, finish_reason)

            return assistant_message

        except Exception as e:
            console.print(f"[red]❌ Ошибка при обращении к LLM: {e}[/red]\n")
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            return None

    def show_welcome(self):
        """Показать приветственное сообщение."""
        welcome_text = """
# 🤖 CLI LLM Бот

Образовательный проект для работы с LLM через OpenRouter API.

**Доступные команды:**
- `/exit` - выход из программы
- `/clear` - очистить историю диалога
- `/stats` - показать статистику сессии
- `/help` - показать эту справку

Начните диалог с вопроса или сообщения!
        """
        console.print(Panel(
            Markdown(welcome_text),
            title="📖 Справка",
            border_style="green",
            padding=(1, 2)
        ))

        if not SYSTEM_PROMPT:
            console.print("[yellow]⚠️  Системный промпт не задан. Отредактируйте SYSTEM_PROMPT в src/bot.py[/yellow]\n")
        else:
            console.print("[green]✓ Системный промпт активен[/green]\n")

    def run(self):
        """Запустить основной цикл бота (REPL)."""
        self.show_welcome()

        try:
            while True:
                try:
                    user_input = console.input("[bold cyan]👤 Вы:[/bold cyan] ").strip()
                except EOFError:
                    break

                if not user_input:
                    continue

                if user_input.startswith("/"):
                    command = user_input.lower()

                    if command == "/exit":
                        console.print("[yellow]👋 До свидания![/yellow]")
                        break

                    elif command == "/clear":
                        self.clear_history()
                        continue

                    elif command == "/stats":
                        self.display_stats()
                        continue

                    elif command == "/help":
                        self.show_welcome()
                        continue

                    else:
                        console.print(f"[red]❌ Неизвестная команда: {user_input}[/red]")
                        console.print("[yellow]Используйте /help для справки[/yellow]\n")
                        continue

                console.print(Panel(
                    user_input,
                    title="👤 Вы",
                    border_style="cyan",
                    padding=(1, 2)
                ))

                self.send_message(user_input)

        except KeyboardInterrupt:
            console.print("\n[yellow]👋 Прервано пользователем. До свидания![/yellow]")

        if self.session_metrics["messages_count"] > 0:
            console.print("\n[bold green]📊 Финальная статистика сессии:[/bold green]")
            self.display_stats()


def main():
    """Точка входа в программу."""
    bot = ChatBot()
    bot.run()


if __name__ == "__main__":
    main()
