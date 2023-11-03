from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import SpinnerColumn
from rich.console import Console
from rich.layout import Layout
from rich import print
import random
import time
from scheduler import PCB

# Gets the width of the console so I can size each column as a percentage so
# the width stays static looking and the "processes" can grow and shrink.
console = Console()
terminal_width = console.width

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

class Queues:
    def __init__(self, new, ready, running, waiting, IO, exited) -> None:
        self.new = new
        self.ready = ready
        self.running = running
        self.waiting = waiting
        self.IO = IO
        self.exited = exited

    def generate_table(self) -> Table:
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
        table.add_row(*make_row("New", self.new), end_section=True)
        table.add_row(*make_row("Ready", self.ready), end_section=True)
        table.add_row(*make_row("Running", self.running), end_section=True)
        table.add_row(*make_row("Waiting", self.waiting), end_section=True)
        table.add_row(*make_row("IO", self.IO), end_section=True)
        table.add_row(*make_row("Exit", self.exited), end_section=True)
        return table

    def __rich__(self) -> Panel:
        return Panel(self.generate_table())

class Header:
    def __init__(self, clock_tick) -> None:
        self.clock_tick = clock_tick

    def create_header(self) -> Text:
        header = Text(f"Clock Tick: {self.clock_tick}", style="yellow", justify="center")
        return header
    
    def __rich__(self) -> Panel:
        return Panel(self.create_header())

def RenderScreen(new, ready, running, waiting, IO, exited, clock_tick, s_time = 0) -> Layout:
    layout = Layout()

    layout.split(
        Layout(name="header", size=1),
        Layout(name="main"),
    )

    layout["main"].split_column(
        Layout(name="top"), 
        Layout(name="bottom"),
    )

    layout['top'].ratio = 1
    layout['bottom'].ratio = 1

    header = Header(clock_tick)
    table = Queues(new, ready, running, waiting, IO, exited)

    layout['header'].update(header)
    layout['top'].update(table)
    # print(header)
    # print(table)

    return layout
    


if __name__ == "__main__":
    b1 = [10, 16, 10, 17, 9, 15, 8, 15, 10, 15, 9, 15, 10, 17, 11, 15, 8, 17, 10]
    b2 = [11, 16, 9, 16, 10, 15, 8, 16, 8, 17, 10, 15, 11, 17, 8, 17, 11, 16, 8]
    b3 = [9, 16, 10, 15, 11, 16, 10, 16, 11, 15, 10, 15, 10, 17, 11, 16, 10]
    b4 = [9, 16, 9, 15, 8, 15, 9, 15, 9, 16, 10, 15, 10, 16, 8, 17, 8, 16, 9, 17, 8, 16, 11]
    p1 = PCB(0, "p2", b1, 0)
    p2 = PCB(1, "p1", b2, 0)
    p3 = PCB(2, "p3", b3, 1)
    p4 = PCB(3, "p1", b4, 1)

    new = [p3, p4]
    ready = []
    running = [p2]
    waiting = []
    io = [p1]
    exited = []

    # """
    # This is how "rich" looks like its animated. The `Live` method keeps calling
    # the `generate_table()` function 40 times in this case with a small sleep in
    # between. I haven't experimented with the refresh_per_second value, so I don't know.
    # """
    with Live(RenderScreen(new, ready, running, waiting, io, exited, random.randint(1, 50)), refresh_per_second=4) as live:
        live.update(RenderScreen(new, ready, running, waiting, io, exited, random.randint(1, 50)))
        time.sleep(1)
