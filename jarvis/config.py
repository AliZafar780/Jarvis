"""Configuration management for Jarvis."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Jarvis configuration settings."""

    # Ollama settings
    ollama_host: str = field(default_factory=lambda: os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3.2"))

    # Voice settings
    voice_engine: str = field(default_factory=lambda: os.getenv("VOICE_ENGINE", "pyttsx3"))
    voice_rate: int = field(default_factory=lambda: int(os.getenv("VOICE_RATE", "175")))
    voice_volume: float = field(default_factory=lambda: float(os.getenv("VOICE_VOLUME", "1.0")))

    # Wake word
    wake_word: str = field(default_factory=lambda: os.getenv("WAKE_WORD", "jarvis").lower())

    # Paths
    downloads_path: Path = field(default_factory=lambda: Path(os.getenv("DOWNLOADS_PATH", "~/Downloads")).expanduser())
    documents_path: Path = field(default_factory=lambda: Path(os.getenv("DOCUMENTS_PATH", "~/Documents")).expanduser())

    # Memory settings
    memory_enabled: bool = True
    memory_path: Path = field(default_factory=lambda: Path(__file__).parent / "memory")

    # API Keys (optional)
    openweather_api_key: str = field(default_factory=lambda: os.getenv("OPENWEATHER_API_KEY", ""))
    news_api_key: str = field(default_factory=lambda: os.getenv("NEWS_API_KEY", ""))

    def __post_init__(self):
        """Ensure paths exist."""
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.downloads_path.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()
