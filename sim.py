'''
Command Line tools for the CPU Scheduler simulation. 
python sim.py --help for usage.
Processes passed as a input file should follow the patterns found in test_data.
'''

import argparse
from scheduler import Scheduler

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Simulate a system with scheduling and CPU/IO management.')
    
    # Add command-line arguments
    parser.add_argument('input', help='Input file for simulation')
    parser.add_argument('--sched', default='FCFS', help="Scheduling algorithm (default: 'FCFS', must be one of ['FCFS', 'PB', 'RR']")
    parser.add_argument('--cpus', type=int, default=2, help='Number of CPUs (default: 2)')
    parser.add_argument('--ios', type=int, default=2, help='Number of IO devices (default: 2)')
    parser.add_argument('--speed', type=float, default=0.1, help='Number of seconds between each clock tick (default: 0.1)')
    parser.add_argument('--time_slice', type=int, default=5, help='Time Slice for Round Robin (default: 5)')
    parser.add_argument('--csv_file', type=str, default="", help='saves the run info for the given simulation, (ex: --csv_file FCFS_CPU_heavy_L)')
    
    return parser.parse_args()
    

if __name__ == "__main__":

    args = parse_command_line_args()

    scheduling_algorithm = args.sched
    num_cpus = args.cpus
    num_ios = args.ios
    speed = args.speed
    time_slice = args.time_slice
    csv_file = args.csv_file

    simulation = Scheduler(cores=num_cpus, io_devices=num_ios)
    simulation.readData(args.input)
    simulation.schedule(mode=scheduling_algorithm, 
                            time_slice=time_slice, speed=speed)

    if csv_file != "":
        simulation.saveRunInfo(csv_file=csv_file)
