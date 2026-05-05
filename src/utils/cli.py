from rich.console import Console

def spinner_status(message: str):
    """
    Context manager for Rich console spinner status.
    
    Usage:
        with spinner_status("Processing...") as status:
            do_work()
            status.update("Step 2...")
    """
    console = Console()
    return console.status(
        f"[bold green]{message}",
        spinner="dots",
        spinner_style="status.spinner",
        speed=1.0
    )