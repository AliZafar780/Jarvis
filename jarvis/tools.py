"""System control, file operations, web search, and utility tools."""

import ast
import os
import shlex
import subprocess
import platform
import psutil
import webbrowser
import json
import operator
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table

from jarvis.config import config

console = Console()


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    message: str
    data: Optional[Any] = None


class SystemTools:
    """System control and information tools."""

    @staticmethod
    def get_system_info() -> ToolResult:
        """Get system information."""
        try:
            info = {
                "platform": platform.platform(),
                "processor": platform.processor(),
                "architecture": platform.architecture()[0],
                "hostname": platform.node(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                    "available": f"{psutil.virtual_memory().available / (1024**3):.2f} GB",
                    "percent": f"{psutil.virtual_memory().percent}%"
                },
                "disk": {
                    "total": f"{psutil.disk_usage('/').total / (1024**3):.2f} GB",
                    "free": f"{psutil.disk_usage('/').free / (1024**3):.2f} GB",
                    "percent": f"{psutil.disk_usage('/').percent}%"
                },
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }

            table = Table(title="System Information")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            for key, value in info.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        table.add_row(f"{key}.{subkey}", str(subvalue))
                else:
                    table.add_row(key, str(value))

            console.print(table)
            return ToolResult(True, "System information retrieved", info)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def list_processes(top_n: int = 10) -> ToolResult:
        """List top processes by CPU usage."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            top_processes = processes[:top_n]

            table = Table(title=f"Top {top_n} Processes by CPU")
            table.add_column("PID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("CPU %", style="yellow")
            table.add_column("Memory %", style="magenta")

            for proc in top_processes:
                table.add_row(
                    str(proc['pid']),
                    str(proc['name']),
                    f"{proc['cpu_percent']:.1f}" if proc['cpu_percent'] else "N/A",
                    f"{proc['memory_percent']:.1f}" if proc['memory_percent'] else "N/A"
                )

            console.print(table)
            return ToolResult(True, f"Listed top {top_n} processes", top_processes)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def kill_process(pid: int) -> ToolResult:
        """Kill a process by PID."""
        try:
            process = psutil.Process(pid)
            name = process.name()
            process.terminate()
            return ToolResult(True, f"Terminated process {name} (PID: {pid})")
        except psutil.NoSuchProcess:
            return ToolResult(False, f"Process {pid} not found")
        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def run_command(command: str, shell: bool = False) -> ToolResult:
        """Run a shell command securely with shell=False and blocked command checking."""
        BLOCKED_COMMANDS = {'rm', 'dd', 'mkfs', 'format', 'shutdown', 'reboot',
                            'del', 'rd', 'poweroff', 'halt', 'init', 'telinit'}
        try:
            parts = shlex.split(command)
            if not parts:
                return ToolResult(False, "Empty command")

            cmd_lower = parts[0].lower()
            # Check the base command (handle paths like /bin/rm)
            base_cmd = os.path.basename(cmd_lower) if '/' in cmd_lower or '\\' in cmd_lower else cmd_lower
            if base_cmd in BLOCKED_COMMANDS:
                return ToolResult(False, f"Command '{parts[0]}' is blocked for security reasons")

            result = subprocess.run(
                parts if not shell else command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout if result.stdout else result.stderr
            success = result.returncode == 0

            if output:
                console.print(f"[dim]{output[:1000]}{'...' if len(output) > 1000 else ''}[/dim]")

            return ToolResult(success, output[:500], {"returncode": result.returncode})

        except subprocess.TimeoutExpired:
            return ToolResult(False, "Command timed out after 30 seconds")
        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def open_application(app_name: str) -> ToolResult:
        """Open an application securely without shell=True."""
        try:
            system = platform.system()

            if system == "Darwin":  # macOS
                subprocess.run(["open", "-a", app_name])
            elif system == "Windows":
                os.startfile(app_name)
            else:  # Linux
                parts = shlex.split(app_name)
                subprocess.run(parts)

            return ToolResult(True, f"Opened {app_name}")

        except Exception as e:
            return ToolResult(False, f"Error opening {app_name}: {e}")

    @staticmethod
    def open_url(url: str) -> ToolResult:
        """Open a URL in browser."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            webbrowser.open(url)
            return ToolResult(True, f"Opened {url}")
        except Exception as e:
            return ToolResult(False, f"Error: {e}")


class FileTools:
    """File system operations."""

    @staticmethod
    def list_directory(path: str = ".") -> ToolResult:
        """List directory contents."""
        try:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                return ToolResult(False, f"Path does not exist: {path}")

            items = []
            for item in p.iterdir():
                item_type = "📁" if item.is_dir() else "📄"
                size = ""
                if item.is_file():
                    size = f"({item.stat().st_size / 1024:.1f} KB)"
                items.append(f"{item_type} {item.name} {size}")

            table = Table(title=f"Contents of {p}")
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Size", style="yellow")

            for item in p.iterdir():
                item_type = "📁" if item.is_dir() else "📄"
                size = ""
                if item.is_file():
                    size = f"{item.stat().st_size / 1024:.1f} KB"
                table.add_row(item_type, item.name, size)

            console.print(table)
            return ToolResult(True, f"Listed {len(items)} items", items)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def read_file(path: str, max_lines: int = 100) -> ToolResult:
        """Read file contents."""
        try:
            p = Path(path).expanduser().resolve()
            if not p.exists():
                return ToolResult(False, f"File not found: {path}")

            content = p.read_text()
            lines = content.split('\n')[:max_lines]

            console.print(f"[cyan]Contents of {p}:[/cyan]")
            console.print("[dim]" + "\n".join(lines) + "[/dim]")

            if len(content.split('\n')) > max_lines:
                console.print(f"[dim]... ({len(content.split('\n')) - max_lines} more lines)[/dim]")

            return ToolResult(True, f"Read {len(lines)} lines", content)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def write_file(path: str, content: str) -> ToolResult:
        """Write content to a file within allowed directories only."""
        ALLOWED_DIRS = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Desktop",
        ]
        try:
            p = Path(path).expanduser().resolve()
            # Ensure file is within one of the allowed directories
            if not any(str(p).startswith(str(allowed.resolve())) for allowed in ALLOWED_DIRS):
                return ToolResult(False, f"Access denied: path must be within Documents, Downloads, or Desktop")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return ToolResult(True, f"Written to {p}")
        except PermissionError:
            return ToolResult(False, "Permission denied: cannot write to that location")
        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def search_files(query: str, path: str = ".") -> ToolResult:
        """Search for files by name."""
        try:
            p = Path(path).expanduser().resolve()
            matches = []

            for item in p.rglob(f"*{query}*"):
                matches.append(str(item.relative_to(p)))

            if matches:
                console.print(f"[green]Found {len(matches)} matches:[/green]")
                for match in matches[:20]:
                    console.print(f"  {match}")
                if len(matches) > 20:
                    console.print(f"  ... and {len(matches) - 20} more")

            return ToolResult(True, f"Found {len(matches)} matches", matches)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")


class WebTools:
    """Web search and browsing tools."""

    @staticmethod
    def search_web(query: str) -> ToolResult:
        """Search the web using DuckDuckGo."""
        try:
            # Using DuckDuckGo HTML interface
            url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.find_all('div', class_='result')[:5]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and snippet_elem:
                    results.append({
                        "title": title_elem.text.strip(),
                        "url": title_elem.get('href', ''),
                        "snippet": snippet_elem.text.strip()
                    })

            if results:
                table = Table(title=f"Search Results: {query}")
                table.add_column("Title", style="cyan")
                table.add_column("Snippet", style="green")

                for r in results:
                    table.add_row(r['title'][:50], r['snippet'][:80])

                console.print(table)

            return ToolResult(True, f"Found {len(results)} results", results)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def get_weather(location: str) -> ToolResult:
        """Get weather information."""
        try:
            # Using wttr.in service (no API key needed)
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            data = response.json()

            current = data['current_condition'][0]
            weather_info = {
                "location": location,
                "temperature_c": current['temp_C'],
                "temperature_f": current['temp_F'],
                "condition": current['weatherDesc'][0]['value'],
                "humidity": current['humidity'],
                "wind": current['windspeedKmph']
            }

            console.print(f"[cyan]Weather in {location}:[/cyan]")
            console.print(f"  Temperature: {weather_info['temperature_c']}°C / {weather_info['temperature_f']}°F")
            console.print(f"  Condition: {weather_info['condition']}")
            console.print(f"  Humidity: {weather_info['humidity']}%")
            console.print(f"  Wind: {weather_info['wind']} km/h")

            return ToolResult(True, f"Weather in {location}: {weather_info['condition']}, {weather_info['temperature_c']}°C", weather_info)

        except Exception as e:
            return ToolResult(False, f"Error: {e}")


class MathSafeEvaluator:
    """Safe mathematical expression evaluator using AST only (no eval())."""
    _OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    @classmethod
    def evaluate(cls, expression: str) -> float:
        """Parse and safely evaluate a mathematical expression."""
        tree = ast.parse(expression.strip(), mode='eval')
        cls._validate(tree)
        return cls._eval_node(tree.body)

    @classmethod
    def _validate(cls, tree: ast.AST):
        """Walk the tree and ensure only safe math nodes are present."""
        allowed_types = {
            ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
            ast.Mod, ast.Pow, ast.USub, ast.UAdd,
        }
        for node in ast.walk(tree):
            if type(node) not in allowed_types:
                raise ValueError(f"Unsupported syntax: {type(node).__name__}")

    @classmethod
    def _eval_node(cls, node: ast.AST) -> float:
        """Recursively evaluate an AST node without using eval()."""
        if isinstance(node, ast.Constant):
            val = node.value
            if isinstance(val, (int, float)):
                return float(val)
            raise ValueError(f"Unsupported constant: {type(val).__name__}")
        if isinstance(node, ast.BinOp):
            op_func = cls._OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported binary operator: {type(node.op).__name__}")
            return op_func(cls._eval_node(node.left), cls._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op_func = cls._OPERATORS.get(type(node.op))
            if op_func is None:
                raise ValueError(f"Unsupported unary operator: {type(node.op).__name__}")
            return op_func(cls._eval_node(node.operand))
        raise ValueError(f"Unsupported node: {type(node).__name__}")


class UtilityTools:
    """Miscellaneous utility tools."""

    @staticmethod
    def get_time() -> ToolResult:
        """Get current time."""
        now = datetime.now()
        time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        console.print(f"[green]Current time: {time_str}[/green]")
        return ToolResult(True, time_str, {"datetime": now})

    @staticmethod
    def copy_to_clipboard(text: str) -> ToolResult:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            return ToolResult(True, "Copied to clipboard")
        except Exception as e:
            return ToolResult(False, f"Error: {e}")

    @staticmethod
    def calculate(expression: str) -> ToolResult:
        """Calculate a mathematical expression safely without eval()."""
        try:
            allowed_chars = set('0123456789+-*/.()eE ')
            if not all(c in allowed_chars for c in expression):
                return ToolResult(False, "Invalid characters in expression")

            result = MathSafeEvaluator.evaluate(expression)
            console.print(f"[green]{expression} = {result}[/green]")
            return ToolResult(True, str(result), {"result": result})

        except (SyntaxError, ValueError, ZeroDivisionError) as e:
            return ToolResult(False, f"Error: {e}")
        except Exception as e:
            return ToolResult(False, f"Error: {type(e).__name__}: {e}")


# Tool registry
TOOLS = {
    "system_info": SystemTools.get_system_info,
    "list_processes": SystemTools.list_processes,
    "kill_process": SystemTools.kill_process,
    "run_command": SystemTools.run_command,
    "open_app": SystemTools.open_application,
    "open_url": SystemTools.open_url,
    "list_dir": FileTools.list_directory,
    "read_file": FileTools.read_file,
    "write_file": FileTools.write_file,
    "search_files": FileTools.search_files,
    "web_search": WebTools.search_web,
    "weather": WebTools.get_weather,
    "time": UtilityTools.get_time,
    "clipboard": UtilityTools.copy_to_clipboard,
    "calculate": UtilityTools.calculate,
}


def execute_tool(tool_name: str, **kwargs) -> ToolResult:
    """Execute a tool by name."""
    if tool_name not in TOOLS:
        return ToolResult(False, f"Unknown tool: {tool_name}")

    try:
        return TOOLS[tool_name](**kwargs)
    except Exception as e:
        return ToolResult(False, f"Tool execution error: {e}")
