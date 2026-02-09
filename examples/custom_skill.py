#!/usr/bin/env python3
"""Examples of creating and registering custom skills."""

from jarvis.skills import Skill, SkillResult, skills


class WeatherSkill(Skill):
    """Custom skill for retrieving weather information."""

    name = "weather_advanced"
    description = "Get detailed weather information for a location"
    triggers = ["weather", "temperature", "forecast"]

    def can_handle(self, command: str) -> bool:
        """Check if this skill can handle the command."""
        return any(trigger in command.lower() for trigger in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        """Execute the weather skill."""
        import re

        # Extract location
        match = re.search(r'(?:in|for|at)\s+([A-Za-z\s]+)', command, re.IGNORECASE)
        location = match.group(1).strip() if match else "your location"

        # For demo, use the basic weather tool
        from jarvis.tools import execute_tool
        result = execute_tool("weather", location=location)

        if result.success:
            return SkillResult(
                True,
                f"Here's the weather for {location}: {result.message}",
                result.data
            )

        return SkillResult(False, f"Couldn't get weather for {location}")


class JokeSkill(Skill):
    """Custom skill that tells programming jokes."""

    name = "jokes"
    description = "Tell programming and tech jokes"
    triggers = ["joke", "funny", "laugh", "humor"]

    JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the developer go broke? Because he used up all his cache!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "Why do Java developers wear glasses? Because they don't C#!",
        "What's a programmer's favorite place? The foo bar!",
    ]

    def can_handle(self, command: str) -> bool:
        return any(trigger in command.lower() for trigger in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        import random
        joke = random.choice(self.JOKES)
        return SkillResult(True, joke)


class GreetingSkill(Skill):
    """Custom skill for time-based personalized greetings."""

    name = "greeting"
    description = "Provide personalized greetings based on time of day"
    triggers = ["hello", "hi", "good morning", "good afternoon", "good evening"]

    def can_handle(self, command: str) -> bool:
        return any(trigger in command.lower() for trigger in self.triggers)

    def execute(self, command: str, **kwargs) -> SkillResult:
        from datetime import datetime

        hour = datetime.now().hour

        if 5 <= hour < 12:
            greeting = "Good morning! Hope you have a productive day ahead!"
        elif 12 <= hour < 17:
            greeting = "Good afternoon! How's your day going?"
        elif 17 <= hour < 22:
            greeting = "Good evening! Time to wind down?"
        else:
            greeting = "Hello! Working late, I see!"

        return SkillResult(True, greeting)


def main():
    """Demonstrate custom skills."""
    print("=== Custom Skills Example ===\n")

    # Register custom skills
    skills.register(WeatherSkill())
    skills.register(JokeSkill())
    skills.register(GreetingSkill())

    print("Registered skills:")
    for skill_help in skills.list_skills():
        print(f"  • {skill_help}")
    print()

    # Test commands
    test_commands = [
        "Hello Jarvis",
        "What's the weather in London?",
        "Tell me a joke",
        "Good morning",
    ]

    for command in test_commands:
        print(f"Command: '{command}'")
        result = skills.execute(command)
        if result:
            print(f"Result: {result.message}")
        else:
            print("No skill handled this command")
        print()


if __name__ == "__main__":
    main()
