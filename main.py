#!/usr/bin/env python3
"""
Jarvis - AI Agent with Ollama, TTS, and System Control

Usage:
    python main.py                    # Chat mode
    python main.py --voice            # Voice-controlled mode
    python main.py --command "..."    # Single command mode
"""

import argparse
import sys
from rich.console import Console

from jarvis.agent import jarvis
from jarvis.llm import OllamaClient
from jarvis.config import config

console = Console()


def check_ollama():
    """Check if Ollama is available."""
    try:
        client = OllamaClient()
        models = client.list_models()
        if config.ollama_model not in models:
            console.print(f"[yellow]Warning: Model '{config.ollama_model}' not found.[/yellow]")
            console.print(f"[dim]Available models: {', '.join(models) if models else 'None'}[/dim]")
            console.print(f"[dim]Install with: ollama pull {config.ollama_model}[/dim]")
            return False
        return True
    except Exception as e:
        console.print(f"[red]Error: Cannot connect to Ollama at {config.ollama_host}[/red]")
        console.print(f"[dim]Error details: {e}[/dim]")
        console.print("\n[yellow]Please ensure Ollama is installed and running:[/yellow]")
        console.print("  1. Install: https://ollama.com/download")
        console.print("  2. Run: ollama serve")
        console.print(f"  3. Pull model: ollama pull {config.ollama_model}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis - AI Agent with Ollama, TTS, and System Control"
    )
    parser.add_argument(
        "--voice", "-v",
        action="store_true",
        help="Enable voice control mode"
    )
    parser.add_argument(
        "--command", "-c",
        type=str,
        help="Execute a single command and exit"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=config.ollama_model,
        help=f"Ollama model to use (default: {config.ollama_model})"
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List available Ollama models"
    )

    args = parser.parse_args()

    # Update config if model specified
    if args.model:
        config.ollama_model = args.model

    # List models
    if args.list_models:
        client = OllamaClient()
        models = client.list_models()
        console.print("[cyan]Available Ollama models:[/cyan]")
        for model in models:
            console.print(f"  • {model}")
        return

    # Check Ollama connection
    if not check_ollama():
        if not args.command:  # Allow single commands even if check fails
            sys.exit(1)

    # Execute single command
    if args.command:
        response = jarvis.process_command(args.command, use_voice=False)
        console.print(response)
        return

    # Run interactive mode
    try:
        jarvis.run(voice=args.voice)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted. Goodbye![/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    main()
