#!/usr/local/bin/python3
"""
Demonstrates a dynamic Layout
"""

from datetime import datetime
from time import sleep
# from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.table import Table, Column
from rich.panel import Panel
from rich.console import Group
import random
import json
import sys,os

stock_data = []

with open('stocks.json') as f:
    data = f.read()
    stock_data = json.loads(data)

console = Console()
layout = Layout()

layout.split(
    Layout(name="header", size=1),
    Layout(name="main"),
    Layout(size=3, name="footer"),
)

layout["main"].split_row(
    Layout(name="left"), 
    # Layout(name="center"), 
    Layout(name="right"),
    #direction="horizontal"
)

layout['left'].ratio = 1
# layout['center'].ratio = 1
layout['right'].ratio = 1

# class Queues:
#     """Shows the current usage of the queues."""
#     def __init__(self, processes) -> None:
#         self.queues = processes

#     def build_table(self):
#         table = Table(title="Queues")
#         new = Column()
#         for process in self.queues["new"]:
#             data = Panel(process)
#             new.append(data)

#         table.add_column("New", justify="center", style="blue", no_wrap=True)
#         table.add_row(new)

#         # grid.add_column("New", justify="center", style="blue", no_wrap=True)
#         # grid.add_column("Ready", justify="center", style="green", no_wrap=True)
#         # grid.add_column("Running", justify="center", style="yellow", no_wrap=True)
#         # grid.add_column("Waiting", justify="center", style="magenta", no_wrap=True)
#         # grid.add_column("Exited", justify="center", style="red", no_wrap=True)

#         # for name, queue in self.queues.items():
#         #     for process in queue:
#         #       grid[name].add_row(str(process))

#         return table
    
#     def __rich__(self) -> Panel:
#         return Panel(self.build_table())

class Bursts:
    """Shows the current usage of the queues."""
    def __init__(self, processes) -> None:
        self.queues = processes

    def build_table(self):
        table = Table(title="Bursts")
        table.add_column("PID", justify="center", style="blue", no_wrap=True)
        table.add_column("T-", justify="center", style="yellow", no_wrap=True)

        for process in self.queues["running"]:
            table.add_row(str(process), str(random.randint(1, 50)))

        return table
    
    def __rich__(self) -> Panel:
        return Panel(self.build_table())

class Resources:
    def __init__(self, cores, processes):
        self.min = 1
        self.max = cores
        self.size = random.randint(self.min,self.max)
        self.bar = ""

    def generate_buffer(self):
        self.bar = ""
        adjust = random.randint(-4,4)
        for i in range(self.size+adjust):
            self.bar += ' '

    def __rich__(self) -> Panel:
        self.generate_buffer()
        return Panel(f'[green on #00FF00]{self.bar}', title="Buffer")
    
# class Test:
#     def generate_grid(self):
#         # Define the data for your columns
#         column1 = ["Item 1", "Item 2", "Item 3"]
#         column2 = ["Description 1", "Description 2", "Description 3"]
#         column3 = ["Price 1", "Price 2", "Price 3"]

#         # Calculate the maximum number of rows in any column
#         max_rows = max(len(column1), len(column2), len(column3))

#         grid = Table.grid(expand=True)
#         # Create a grid with three columns
#         for row in range(max_rows):
#             if row < len(column1):
#                 grid.add_row(column1[row], style="white on blue")
#             if row < len(column2):
#                 grid.add_cell(column2[row], style="white on green")
#             if row < len(column3):
#                 grid.add_cell(column3[row], style="white on red")
        
#         return grid
    
#     def __rich__(self) -> Panel:
#         return Panel(self.generate_grid())
    
processes = {
    'new': ['P9'],
    'ready': ['P3', 'P4'],
    'running': ['P2', 'P6', 'P7', 'P8'],
    'waiting': ['P5'],
    'exited': ['P1']
}

# T = Test()
# Q = Queues(processes)
B = Bursts(processes)

# layout["left"].update(Q)
# layout["center"].update()
layout["right"].update(B)

with Live(layout, screen=True, redirect_stderr=False) as live:
    try:
        while True:
            sleep(0.9)
    except KeyboardInterrupt:
        pass