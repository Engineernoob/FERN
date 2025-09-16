from rich.console import Console
from datetime import datetime

console = Console()

def log_step(emoji: str, msg: str, style: str = "bold green"):
    console.print(f"{emoji} [ {datetime.now().strftime('%H:%M:%S')} ] [ {style}]{msg}[/]")

def log_info(msg: str):
    log_step("ℹ️", msg, "cyan")

def log_success(msg: str):
    log_step("✅", msg, "green")

def log_warn(msg: str):
    log_step("⚠️", msg, "yellow")

def log_error(msg: str):
    log_step("❌", msg, "red")

def log_progress(msg: str):
    log_step("🌱", msg, "magenta")
