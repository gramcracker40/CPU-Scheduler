from rich import print
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.progress import SpinnerColumn
from rich.console import Console
from rich.layout import Layout
from pcb import PCB

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

    # text = Text(processes)
    # text.rstrip_end(30)
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
        table = Table(show_header=False, padding=(1))
        #table.add_column("Queue", style="bold yellow on blue dim", width=int(terminal_width*.1))
        table.add_column("Queue", style="bold yellow", width=int(terminal_width*.2))
        table.add_column("Processes", width=int(terminal_width*.9))
        table.add_row(*make_row("New", self.new), end_section=True)
        table.add_row(*make_row("Ready", self.ready), end_section=True)
        table.add_row(*make_row("Running", self.running), end_section=True)
        table.add_row(*make_row("Waiting", self.waiting), end_section=True)
        table.add_row(*make_row("IO", self.IO), end_section=True)
        table.add_row(*make_row("Exit", self.exited), end_section=True)
        return table

    def __rich__(self) -> Panel:
        return Panel(self.generate_table(), title="Queues")

class Header:
    def __init__(self, clock_tick) -> None:
        self.clock_tick = clock_tick

    def create_header(self) -> Text:
        header = Text(f"Clock Tick: {self.clock_tick}", style="yellow", justify="center")
        return header
    
    def __rich__(self) -> Panel:
        return Panel(self.create_header())
    

class Messages:
    def __init__(self, messages):
        self.messages = messages  # Initialize an empty list for messages

    def add_message(self, message, style="green"):
        self.messages.insert(0, {"message": message, "style": style})  # Insert the message with style at the beginning of the list

    def generate_message_text(self):
        message_text = Text()
        for message_info in self.messages:
            message_text.append(f"{message_info['message']}\n", style=message_info["style"])

        return message_text

    def __rich__(self):
        return Panel(self.generate_message_text(), title="Messages")
    
class JobStats:
    def __init__(self, pcbs, mode) -> None:
        self.pcbs = pcbs
        self.mode = mode

    def create_row(self, pcb):
        row = []
        if self.mode == "PB":
            row = [str(pcb.pid), str(pcb.priority), str(pcb.arrivalTime), str(pcb.processTime), str(pcb.readyQueueTime), str(pcb.waitingQueueTime)]
        else:
            row = [str(pcb.pid), str(pcb.arrivalTime), str(pcb.processTime), str(pcb.readyQueueTime), str(pcb.waitingQueueTime)]
        return row

    def create_table(self) -> Table:
        table = Table()
        table.add_column("Job", style="bold blue", width=int(terminal_width*.9))
        if self.mode == "PB":
            table.add_column("Priority", style="bold magenta", width=int(terminal_width*.9))
        table.add_column("Arrival Time", width=int(terminal_width*.9))
        table.add_column("Turn Around Time", width=int(terminal_width*.9))
        table.add_column("Time In Ready Queue", width=int(terminal_width*.9))
        table.add_column("Time In Waiting Queue", width=int(terminal_width*.9))
        for pcb in self.pcbs:
            table.add_row(*self.create_row(pcb), end_section=True)
        return table

    def __rich__(self) -> Panel:
        return Panel(self.create_table(), title="[bold yellow]Job Stats[/bold yellow]")

class Stats:
    def __init__(self, pcbs, total_time, cores) -> None:
        self.pcbs = pcbs
        self.total_time = total_time
        self.num_cores = cores
        self.cpu_util = 0
        self.atat = 0
        self.atrq = 0
        self.atwq = 0

    def calculate_stats(self):
        count = 0
        for pcb in self.pcbs:
            self.cpu_util += pcb.runningQueueTime
            self.atat += (pcb.timeExited - pcb.arrivalTime)
            self.atrq += pcb.readyQueueTime
            self.atwq += pcb.waitingQueueTime
            count += 1
        
        self.cpu_util = ((self.cpu_util / self.num_cores) / self.total_time) * 100
        self.cpu_util = round(self.cpu_util, 2)

        if self.cpu_util >= 75:
            self.cpu_util = f"[bold red]{self.cpu_util}%[/bold red]"
        elif self.cpu_util >= 25:
            self.cpu_util = f"[bold dark_orange]{self.cpu_util}%[/bold dark_orange]"
        else:
            self.cpu_util = f"[bold green]{self.cpu_util}%[/bold green]"

        if count != 0:
            self.atat /= count
            self.atrq /= count
            self.atwq /= count

    def create_row(self):
        self.calculate_stats()
        return [self.cpu_util, str(self.atat), str(self.atrq), str(self.atwq)]

    def create_table(self) -> Table:
        table = Table()
        table.add_column("CPU Utilization", width=int(terminal_width*.9))
        table.add_column("Average Turn Around Time", width=int(terminal_width*.9))
        table.add_column("Average Time In Ready Queue", width=int(terminal_width*.9))
        table.add_column("Average Time In Waiting Queue", width=int(terminal_width*.9))
        table.add_row(*self.create_row(), end_section=True)
        return table

    def __rich__(self) -> Panel:
        return Panel(self.create_table(), title="[bold yellow]Stats[/bold yellow]")
    
class ExtraStats:
    def __init__(self, pcbs, total_time, devices) -> None:
        self.pcbs = pcbs
        self.total_time = total_time
        self.num_devices = devices
        self.io_util = 0
        self.atrnq = 0
        self.atioq = 0

    def calculate_stats(self):
        count = 0
        for pcb in self.pcbs:
            self.io_util += pcb.ioQueueTime
            self.atrnq += pcb.runningQueueTime
            self.atioq += pcb.ioQueueTime
            count += 1

        self.io_util = ((self.io_util / self.num_devices) / self.total_time) * 100
        self.io_util = round(self.io_util, 2)

        if self.io_util >= 75:
            self.io_util = f"[bold red]{self.io_util}%[/bold red]"
        elif self.io_util >= 25:
            self.io_util = f"[bold dark_orange]{self.io_util}%[/bold dark_orange]"
        else:
            self.io_util = f"[bold green]{self.io_util}%[/bold green]"

        if count != 0:
            self.atrnq /= count
            self.atioq /= count

    def create_row(self):
        self.calculate_stats()
        return [self.io_util, str(self.total_time), str(self.atrnq), str(self.atioq)]

    def create_table(self) -> Table:
        table = Table()
        table.add_column("IO Utilization", width=int(terminal_width*.9))
        table.add_column("Total Time", width=int(terminal_width*.9))
        table.add_column("Average Time In Running Queue", width=int(terminal_width*.9))
        table.add_column("Average Time In IO Queue", width=int(terminal_width*.9))
        table.add_row(*self.create_row(), end_section=True)
        return table

    def __rich__(self) -> Panel:
        return Panel(self.create_table(), title="[bold yellow]Extra Stats[/bold yellow]")


def RenderScreen(new, ready, running, waiting, IO, exited, clock_tick, messages, s_time = 0) -> Layout:
    layout = Layout()

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main"),
    )

    layout["main"].split_column(
        Layout(name="top"), 
        Layout(name="bottom"),
    )

    layout['top'].ratio = 2
    layout['bottom'].ratio = 1

    header = Header(clock_tick)
    table = Queues(new, ready, running, waiting, IO, exited)
    bottom = Messages(messages)

    layout['header'].update(header)
    layout['top'].update(table)
    layout['bottom'].update(bottom)

    return layout

def RenderStats(exited, total_time, cores, devices, mode):
    print("\n")
    stats = Stats(exited, total_time, cores)
    print(stats)
    print("\n")

    extra_stats = ExtraStats(exited, total_time, devices)
    print(extra_stats)
    print("\n")

    job_stats = JobStats(exited, mode)
    print(job_stats)
