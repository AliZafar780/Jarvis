"""Ollama LLM integration for Jarvis."""

import json
from typing import AsyncIterator, Dict, List, Optional, Callable
import ollama
from rich.console import Console

from jarvis.config import config

console = Console()


class OllamaClient:
    """Client for Ollama LLM interactions."""

    SYSTEM_PROMPT = """You are Jarvis, an advanced AI assistant with system control capabilities.
You have access to various tools and can execute commands on the user's system.
Be helpful, concise, and professional. When executing system commands, be careful and confirm destructive actions.

Available capabilities:
- File system operations (read, write, list, delete files)
- Process management (list, kill processes)
- Web search and browsing
- System information (CPU, memory, disk usage)
- Application launching
- Clipboard operations
- Notifications
- Code execution (Python)

Always respond in a helpful, slightly witty manner like a personal assistant.
If you need to use a tool, indicate it clearly in your response.
"""

    def __init__(self, model: Optional[str] = None):
        self.model = model or config.ollama_model
        self.client = ollama.Client(host=config.ollama_host)
        self.history: List[Dict[str, str]] = []
        self.console = Console()

    def chat(self, message: str, tools: Optional[List[Dict]] = None) -> str:
        """Send a chat message and get response."""
        try:
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                *self.history,
                {"role": "user", "content": message}
            ]

            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options={
                    "temperature": 0.7,
                    "num_predict": 2048,
                }
            )

            assistant_message = response['message']['content']

            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": assistant_message})

            # Keep history manageable
            if len(self.history) > 20:
                self.history = self.history[-20:]

            return assistant_message

        except Exception as e:
            console.print(f"[red]Error communicating with Ollama: {e}[/red]")
            return f"I'm having trouble connecting to my brain. Error: {e}"

    async def chat_stream(self, message: str) -> AsyncIterator[str]:
        """Stream chat response."""
        try:
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                *self.history,
                {"role": "user", "content": message}
            ]

            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={
                    "temperature": 0.7,
                    "num_predict": 2048,
                }
            )

            full_response = ""
            for chunk in stream:
                content = chunk['message']['content']
                full_response += content
                yield content

            # Update history after complete
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": full_response})

            if len(self.history) > 20:
                self.history = self.history[-20:]

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            yield f"I'm having trouble connecting to my brain. Error: {e}"

    def clear_history(self):
        """Clear conversation history."""
        self.history = []
        console.print("[yellow]Conversation history cleared.[/yellow]")

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            models = self.client.list()
            return [model['name'] for model in models['models']]
        except Exception as e:
            console.print(f"[red]Error listing models: {e}[/red]")
            return []

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate text from a prompt."""
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                system=system or self.SYSTEM_PROMPT,
                options={
                    "temperature": 0.7,
                    "num_predict": 2048,
                }
            )
            return response['response']
        except Exception as e:
            console.print(f"[red]Error generating: {e}[/red]")
            return f"Error: {e}"
