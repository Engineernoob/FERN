# fern/tools/banner.py
from rich.console import Console

console = Console()

FERN_BANNER = r"""
 ______   ______     ______     __   __    
/\  ___\ /\  ___\   /\  == \   /\ "-.\ \   
\ \  __\ \ \  __\   \ \  __<   \ \ \-.  \  
 \ \_\    \ \_____\  \ \_\ \_\  \ \_\\"\_\ 
  \/_/     \/_____/   \/_/ /_/   \/_/ \/_/ 
                                                                                                                 
"""

def show_banner():
    console.print(FERN_BANNER, style="bold green")
    console.print("🌱 [bold green]FERN – Full-stack Engineering Reinforcement Navigator[/]")
    console.print("[cyan]Talk to FERN while it builds, tests, and improves your code.[/]\n")
