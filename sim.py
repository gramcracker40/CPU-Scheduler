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
    args = parser.parse_args()
    
    return args
    

if __name__ == "__main__":

    args = parse_command_line_args()

    scheduling_algorithm = args.sched
    num_cpus = args.cpus
    num_ios = args.ios
    speed = args.speed
    time_slice = args.time_slice

    simulation = Scheduler(cores=num_cpus, io_devices=num_ios)
    simulation.readData(args.input)
    simulation.schedule(mode=scheduling_algorithm, 
                            time_slice=time_slice, speed=speed)

