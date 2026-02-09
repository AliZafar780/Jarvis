"""Extensible skills system for Jarvis."""

import json
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class SkillResult:
    """Result of skill execution."""
    success: bool
    message: str
    data: Optional[Any] = None


class Skill(ABC):
    """Base class for Jarvis skills."""

    name: str = ""
    description: str = ""
    triggers: List[str] = []

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check if this skill can handle the command."""
        pass

    @abstractmethod
    def execute(self, command: str, **kwargs) -> SkillResult:
        """Execute the skill."""
        pass

    def get_help(self) -> str:
        """Get help text for this skill."""
        return f"{self.name}: {self.description}"


class CodeExecutionSkill(Skill):
    """Execute Python code safely."""

    name = "code"
    description = "Execute Python code"
    triggers = ["run code", "execute code", "python", "calculate"]

    def can_handle(self, command: str) -> bool:
        return any(trigger in command.lower() for trigger in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        """Execute Python code in a restricted environment."""
        # Extract code from command
        code = self._extract_code(command)

        if not code:
            return SkillResult(False, "No code found in command")

        try:
            # Create safe globals
            safe_globals = {
                "__builtins__": {
                    "len": len,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "pow": pow,
                    "divmod": divmod,
                    "print": print,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "tuple": tuple,
                }
            }

            # Execute code
            result = eval(code, safe_globals, {})

            return SkillResult(
                True,
                f"Result: {result}",
                {"result": result}
            )

        except Exception as e:
            return SkillResult(False, f"Error: {e}")

    def _extract_code(self, command: str) -> Optional[str]:
        """Extract code from natural language command."""
        # Try to find code in backticks
        match = re.search(r'`{3}(?:python)?\s*\n?(.*?)\n?`{3}', command, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try to extract after "code" or "calculate"
        patterns = [
            r'(?:run|execute)\s+(?:python\s+)?code[:\s]+(.+)',
            r'calculate[:\s]+(.+)',
            r'python[:\s]+(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None


class ReminderSkill(Skill):
    """Set reminders."""

    name = "reminder"
    description = "Set reminders and alarms"
    triggers = ["remind me", "reminder", "alarm"]

    def can_handle(self, command: str) -> bool:
        return any(trigger in command.lower() for trigger in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        """Set a reminder."""
        # Extract reminder details
        match = re.search(
            r'remind\s+me\s+(?:to\s+)?(.+?)(?:\s+(?:in|at|on)\s+(.+))?$',
            command,
            re.IGNORECASE
        )

        if match:
            reminder_text = match.group(1).strip()
            time_spec = match.group(2).strip() if match.group(2) else "soon"

            # In a real implementation, this would schedule the reminder
            return SkillResult(
                True,
                f"I'll remind you to {reminder_text} {time_spec}",
                {"reminder": reminder_text, "time": time_spec}
            )

        return SkillResult(False, "Could not parse reminder")


class NoteTakingSkill(Skill):
    """Take and retrieve notes."""

    name = "notes"
    description = "Take notes and retrieve them"
    triggers = ["note", "write down", "remember that", "what did i note"]

    def __init__(self):
        self.notes: List[Dict] = []

    def can_handle(self, command: str) -> bool:
        return any(trigger in command.lower() for trigger in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        """Handle note commands."""
        command_lower = command.lower()

        if "what did i note" in command_lower or "show notes" in command_lower:
            if not self.notes:
                return SkillResult(True, "You haven't taken any notes yet.")

            notes_text = "\n".join([
                f"{i+1}. {note['content']}"
                for i, note in enumerate(self.notes)
            ])
            return SkillResult(True, f"Your notes:\n{notes_text}", self.notes)

        # Add note
        match = re.search(
            r'(?:note|write\s+down|remember\s+that)[:\s]+(.+)',
            command,
            re.IGNORECASE
        )

        if match:
            note_content = match.group(1).strip()
            self.notes.append({"content": note_content})
            return SkillResult(True, f"Noted: {note_content}")

        return SkillResult(False, "Could not understand note command")


class SkillsManager:
    """Manage and execute skills."""

    def __init__(self):
        self.skills: List[Skill] = []
        self.register_default_skills()

    def register_default_skills(self):
        """Register built-in skills."""
        self.register(CodeExecutionSkill())
        self.register(ReminderSkill())
        self.register(NoteTakingSkill())

    def register(self, skill: Skill):
        """Register a new skill."""
        self.skills.append(skill)
        console.print(f"[dim]Registered skill: {skill.name}[/dim]")

    def find_skill(self, command: str) -> Optional[Skill]:
        """Find a skill that can handle the command."""
        for skill in self.skills:
            if skill.can_handle(command):
                return skill
        return None

    def execute(self, command: str, **kwargs) -> Optional[SkillResult]:
        """Execute a skill for the command."""
        skill = self.find_skill(command)

        if skill:
            console.print(f"[dim]Using skill: {skill.name}[/dim]")
            return skill.execute(command, **kwargs)

        return None

    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return [skill.get_help() for skill in self.skills]


# Global skills manager
skills = SkillsManager()
