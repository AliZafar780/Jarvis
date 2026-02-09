"""Memory management for Jarvis using ChromaDB."""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings

from jarvis.config import config


class Memory:
    """Persistent memory for Jarvis using vector database."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=str(config.memory_path),
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collections
        self.conversations = self.client.get_or_create_collection("conversations")
        self.facts = self.client.get_or_create_collection("facts")
        self.tasks = self.client.get_or_create_collection("tasks")

    def add_conversation(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a conversation entry to memory."""
        doc_id = hashlib.md5(
            f"{datetime.now().isoformat()}{content[:50]}".encode()
        ).hexdigest()

        self.conversations.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[{
                "role": role,
                "timestamp": datetime.now().isoformat(),
                **(metadata or {})
            }]
        )

    def recall_conversations(self, query: str, n_results: int = 5) -> List[Dict]:
        """Recall similar past conversations."""
        results = self.conversations.query(
            query_texts=[query],
            n_results=n_results
        )

        memories = []
        for i, doc in enumerate(results['documents'][0]):
            memories.append({
                "content": doc,
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })

        return memories

    def remember_fact(self, fact: str, category: str = "general"):
        """Remember a fact."""
        doc_id = hashlib.md5(fact.encode()).hexdigest()

        self.facts.add(
            ids=[doc_id],
            documents=[fact],
            metadatas=[{
                "category": category,
                "timestamp": datetime.now().isoformat()
            }]
        )

    def recall_facts(self, query: str, category: Optional[str] = None, n_results: int = 3) -> List[str]:
        """Recall facts related to a query."""
        where_filter = {"category": category} if category else None

        results = self.facts.query(
            query_texts=[query],
            where=where_filter,
            n_results=n_results
        )

        return results['documents'][0] if results['documents'] else []

    def add_task(self, task: str, priority: str = "normal"):
        """Add a task to remember."""
        doc_id = hashlib.md5(
            f"{datetime.now().isoformat()}{task}".encode()
        ).hexdigest()

        self.tasks.add(
            ids=[doc_id],
            documents=[task],
            metadatas=[{
                "priority": priority,
                "created": datetime.now().isoformat(),
                "completed": False
            }]
        )

    def get_tasks(self, completed: bool = False) -> List[Dict]:
        """Get pending or completed tasks."""
        results = self.tasks.get(
            where={"completed": completed}
        )

        tasks = []
        for i, doc in enumerate(results['documents']):
            tasks.append({
                "id": results['ids'][i],
                "task": doc,
                **results['metadatas'][i]
            })

        return tasks

    def complete_task(self, task_id: str):
        """Mark a task as completed."""
        self.tasks.update(
            ids=[task_id],
            metadatas=[{"completed": True}]
        )

    def clear_conversations(self):
        """Clear all conversation history."""
        self.client.delete_collection("conversations")
        self.conversations = self.client.get_or_create_collection("conversations")
