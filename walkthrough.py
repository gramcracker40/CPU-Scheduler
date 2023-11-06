import subprocess

# Define a function to run the given command
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e)

# List of commands from your Markdown file
commands = [
    # FCFS examples
    "python sim.py test_data/CPUS.dat --cpus 1 --ios 1 --sched=FCFS --speed=0.05",
    "python sim.py test_data/IOL.dat --cpus 20 --ios 20 --sched=FCFS --speed=0.0001",

    # Round Robin examples
    "python sim.py test_data/IOS.dat --cpus 1 --ios 1 --sched=RR --speed=0.01 --time_slice 3",
    "python sim.py test_data/CPUL.dat --cpus 20 --ios 20 --sched=RR --speed=0.001 --time_slice 8",

    # Priority based examples
    "python sim.py test_data/PrioSpreadXS.dat --cpus 1 --ios 1 --sched=PB --speed=0.2",
    "python sim.py test_data/PrioSpreadL.dat --cpus 24 --ios 30 --sched=PB --speed=0.001",
]

# Run each command when Enter key is pressed
for command in commands:
    input(f"Press Enter to run the next command: {command}")
    run_command(command)
