from rich import print
from rich.table import Table
from rich.live import Live
import random
import time
from rich.progress import SpinnerColumn
from rich.console import Console

# Gets the width of the console so I can size each column as a percentage so
# the width stays static looking and the "processes" can grow and shrink.
console = Console()
terminal_width = console.width

def get_num():
    """ Helper for make row
    """
    return random.randint(1,99)

def get_proc():
    """Helper for make row
    """
    return f"P{random.randint(1,50)}"

def make_row(name, queue):
    """ This function builds a row with 2 columns. The queue name on the left, and a random number of processes on the right.
        Your job would be to replace this function with something that pulls values out of your pcb in order to show in whichever queue.

    Params:
       name (string) : the name of the queue in the left column
       queue (list of PCB's) : the list of queues
    """
    processes = ""
    for job in queue:
        #processes += str(f"[on green][bold][[/bold][red]{get_proc()}[/red] {get_num()}[bold]][/bold][/on green] ")
        processes += str(f"[bold][[/bold][bold blue]{job.pid} {job.remainingBurst}[/bold blue][bold]][/bold]")
    return [name, processes]

def generate_table(new, ready, running, waiting, IO, exited) -> Table:
    """ 
        - This function returns a `rich` table that displays all the queue contents. How you format that is up to you.
        - The `end_section=True` is what puts a line between rows
        - I left a commented line to show how you can change background colors, but is not the whole table or column or row. You'll see.
        - All I do is call `make_row` with the queue name and my random ranges. The "*" is how you add a "list" as a row, it explodes it basically,
           and since `make_row` returns a list with one entry per column, we need to expand it. 
        - You will probably have to pass in your queues or put this in a class to generate your own table .... or don't. 
    """
    # Create the table
    table = Table(show_header=False)
    #table.add_column("Queue", style="bold yellow on blue dim", width=int(terminal_width*.1))
    table.add_column("Queue", style="bold red", width=int(terminal_width*.1))
    table.add_column("Processes", width=int(terminal_width*.9))
    table.add_row(*make_row("New", new), end_section=True)
    table.add_row(*make_row("Ready", ready), end_section=True)
    table.add_row(*make_row("Running", running), end_section=True)
    table.add_row(*make_row("Waiting", waiting), end_section=True)
    table.add_row(*make_row("IO", IO), end_section=True)
    table.add_row(*make_row("Exit", exited), end_section=True)
    return table


"""
This is how "rich" looks like its animated. The `Live` method keeps calling
the `generate_table()` function 40 times in this case with a small sleep in
between. I haven't experimented with the refresh_per_second value, so I don't know.
"""
with Live(generate_table(), refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)
        live.update(generate_table())

def RenderScreen(new, ready, running, waiting, IO, exited, s_time = 0):
    generate_table(new, ready, running, waiting, IO, exited)
    time.sleep(s_time)