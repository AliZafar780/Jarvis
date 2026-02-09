"""Main orchestrator for the Jarvis AI agent."""

import re
import json
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from jarvis.config import config
from jarvis.llm import OllamaClient
from jarvis.voice import TTS, VoiceRecognizer
from jarvis.tools import execute_tool, ToolResult, TOOLS

console = Console()


class JarvisAgent:
    """Main Jarvis AI Agent."""

    def __init__(self):
        self.llm = OllamaClient()
        self.tts = TTS()
        self.recognizer: Optional[VoiceRecognizer] = None
        self.running = False

    def _speak(self, text: str):
        """Speak text using TTS."""
        self.tts.speak(text)

    def _parse_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse tool calls from LLM response."""
        # Look for tool call patterns like:
        # [TOOL: tool_name] or ```tool\n{"name": "...", "args": {...}}\n```

        # Pattern 1: [TOOL: name, arg1=val1, arg2=val2]
        pattern1 = r'\[TOOL:\s*(\w+)\s*(?:,\s*(\w+)=(\S+))?\]'
        match = re.search(pattern1, text)
        if match:
            tool_name = match.group(1)
            args = {}
            if match.group(2):
                args[match.group(2)] = match.group(3).strip('"\'')
            return {"name": tool_name, "args": args}

        # Pattern 2: JSON format
        json_pattern = r'```(?:tool)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match.strip())
                if "tool" in data or "name" in data:
                    return {
                        "name": data.get("tool") or data.get("name"),
                        "args": data.get("args", data.get("arguments", {}))
                    }
            except json.JSONDecodeError:
                continue

        return None

    def _handle_tool_suggestions(self, text: str) -> str:
        """Handle natural language tool suggestions from LLM."""
        lower_text = text.lower()

        # Check for implied tool usage
        if any(phrase in lower_text for phrase in ["system info", "system information", "cpu usage", "memory usage"]):
            result = execute_tool("system_info")
            return f"\n[System Info executed: {result.message}]"

        if any(phrase in lower_text for phrase in ["list files", "show files", "directory contents"]):
            path = "."
            # Try to extract path
            match = re.search(r'(?:in|from)\s+([~\w/\\.]+)', lower_text)
            if match:
                path = match.group(1)
            result = execute_tool("list_dir", path=path)
            return f"\n[Directory listed: {result.message}]"

        if any(phrase in lower_text for phrase in ["processes", "running processes", "top processes"]):
            result = execute_tool("list_processes")
            return f"\n[Processes listed: {result.message}]"

        if any(phrase in lower_text for phrase in ["what time", "current time", "what is the time"]):
            result = execute_tool("time")
            return f"\n[Time: {result.message}]"

        if any(phrase in lower_text for phrase in ["weather in", "temperature in"]):
            # Extract location
            match = re.search(r'(?:in|for)\s+([A-Za-z\s]+)', text)
            if match:
                location = match.group(1).strip()
                result = execute_tool("weather", location=location)
                return f"\n[Weather: {result.message}]"

        return ""

    def process_command(self, command: str, use_voice: bool = True) -> str:
        """Process a user command."""
        # Pre-process for direct tool commands
        command_lower = command.lower().strip()

        # Handle special commands
        if command_lower in ["exit", "quit", "goodbye"]:
            self.running = False
            response = "Goodbye! Have a great day!"
            if use_voice:
                self._speak(response)
            return response

        if command_lower in ["clear", "clear history"]:
            self.llm.clear_history()
            response = "Conversation history cleared."
            if use_voice:
                self._speak(response)
            return response

        # Direct tool execution shortcuts
        if command_lower.startswith("run "):
            cmd = command[4:]
            result = execute_tool("run_command", command=cmd)
            response = f"Command executed. {result.message}"
            if use_voice:
                self._speak(response)
            return response

        if command_lower.startswith("open "):
            app = command[5:]
            result = execute_tool("open_app", app_name=app)
            response = result.message
            if use_voice:
                self._speak(response)
            return response

        if command_lower.startswith("search "):
            query = command[7:]
            result = execute_tool("web_search", query=query)
            response = f"Search results: {result.message}"
            if use_voice:
                self._speak(response)
            return response

        # Generate context-aware prompt for LLM
        tools_context = """
Available tools you can suggest:
- system_info: Get system information
- list_processes: List running processes
- kill_process: Kill a process (requires pid)
- run_command: Execute shell command
- open_app: Open an application
- open_url: Open URL in browser
- list_dir: List directory contents
- read_file: Read a file
- write_file: Write to a file
- search_files: Search for files
- web_search: Search the web
- weather: Get weather (requires location)
- time: Get current time
- clipboard: Copy to clipboard
- calculate: Calculate expression

When you want to use a tool, include it in your response like:
[TOOL: tool_name, param=value]
"""

        enhanced_prompt = f"{tools_context}\n\nUser command: {command}\n\nRespond naturally. If you need to use a tool, mention it clearly."

        # Get LLM response
        response = self.llm.chat(enhanced_prompt)

        # Check for and execute tool calls
        tool_call = self._parse_tool_call(response)
        if tool_call:
            result = execute_tool(tool_call["name"], **tool_call.get("args", {}))
            # Get follow-up response with tool results
            follow_up = self.llm.chat(
                f"The tool '{tool_call['name']}' returned: {result.message}. "
                f"Please provide a natural response to the user about this result."
            )
            response = follow_up

        # Also check for implied tool usage
        tool_result = self._handle_tool_suggestions(response)
        if tool_result:
            response += tool_result

        # Speak response if voice enabled
        if use_voice:
            self._speak(response)

        return response

    def voice_mode(self):
        """Run in voice-controlled mode."""
        console.print(Panel(
            Text("Voice Mode Activated", style="bold cyan"),
            subtitle=f"Say '{config.wake_word}' to activate"
        ))

        self._speak(f"Voice mode activated. Say {config.wake_word} to get my attention.")

        self.recognizer = VoiceRecognizer()

        while self.running:
            try:
                # Listen for wake word
                if self.recognizer.listen_for_wake_word():
                    self._speak("Yes?")

                    # Listen for command
                    command = self.recognizer.listen_command()

                    if command:
                        console.print(f"[cyan]Command: {command}[/cyan]")
                        response = self.process_command(command, use_voice=True)
                        console.print(f"[green]Jarvis: {response}[/green]")

            except KeyboardInterrupt:
                console.print("\n[yellow]Voice mode paused. Press Ctrl+C again to exit.[/yellow]")
                try:
                    input("Press Enter to continue voice mode...")
                except KeyboardInterrupt:
                    self.running = False
                    break

    def chat_mode(self):
        """Run in interactive chat mode."""
        console.print(Panel(
            Text("Chat Mode", style="bold cyan"),
            subtitle="Type your commands or 'exit' to quit"
        ))

        self._speak("Jarvis is ready. How can I help you?")

        while self.running:
            try:
                command = console.input("[bold cyan]You: [/bold cyan]").strip()

                if not command:
                    continue

                response = self.process_command(command, use_voice=False)

                # Print response with formatting
                console.print(f"[bold green]Jarvis: [/bold green]{response}")

            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")

    def run(self, voice: bool = False):
        """Run the agent."""
        self.running = True

        # Welcome message
        welcome = Panel(
            Text("JARVIS", style="bold cyan", justify="center") +
            Text("\nAI Agent with Ollama, TTS, and System Control", style="dim", justify="center"),
            subtitle="v1.0.0 | Powered by Ollama"
        )
        console.print(welcome)

        if voice:
            self.voice_mode()
        else:
            self.chat_mode()

        console.print("[yellow]Goodbye![/yellow]")


# Create singleton instance
jarvis = JarvisAgent()
