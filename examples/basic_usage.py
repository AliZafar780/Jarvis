#!/usr/bin/env python3
"""Basic usage examples for Jarvis."""

from jarvis.llm import OllamaClient
from jarvis.tools import execute_tool
from jarvis.voice import TTS


def example_chat():
    """Example: Simple chat with LLM."""
    print("=== Chat Example ===")
    client = OllamaClient()

    response = client.chat("What is the capital of France?")
    print(f"Response: {response}\n")


def example_tools():
    """Example: Using system tools."""
    print("=== Tools Example ===")

    # Get system info
    result = execute_tool("system_info")
    print(f"System Info: {result.message}\n")

    # List current directory
    result = execute_tool("list_dir", path=".")
    print(f"Directory: {result.message}\n")

    # Get time
    result = execute_tool("time")
    print(f"Time: {result.message}\n")


def example_voice():
    """Example: Text-to-Speech."""
    print("=== Voice Example ===")

    tts = TTS()
    tts.speak("Hello! I am Jarvis, your AI assistant.")

    # Wait for speech to complete
    import time
    time.sleep(3)


def example_custom_prompt():
    """Example: Custom prompt generation."""
    print("=== Custom Prompt Example ===")

    client = OllamaClient()

    # Generate code
    prompt = "Write a Python function to calculate fibonacci numbers"
    response = client.generate(prompt)
    print(f"Generated code:\n{response}\n")


def example_memory():
    """Example: Using memory."""
    print("=== Memory Example ===")

    from jarvis.memory import Memory

    memory = Memory()

    # Remember something
    memory.remember_fact("My favorite color is blue", category="preferences")
    memory.remember_fact("I work as a software engineer", category="personal")

    # Recall
    facts = memory.recall_facts("What do I like?")
    print(f"Recalled facts: {facts}\n")


if __name__ == "__main__":
    import sys

    examples = {
        "chat": example_chat,
        "tools": example_tools,
        "voice": example_voice,
        "prompt": example_custom_prompt,
        "memory": example_memory,
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("Available examples:")
        for name in examples:
            print(f"  python examples/basic_usage.py {name}")
