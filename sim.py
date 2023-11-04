import argparse
from scheduler import Scheduler

def parse_command_line_args():
    parser = argparse.ArgumentParser(description='Simulate a system with scheduling and CPU/IO management.')
    
    # Add command-line arguments
    parser.add_argument('input', help='Input file for simulation')
    parser.add_argument('--sched', default='FCFS', help='Scheduling algorithm (default: FCFS)')
    parser.add_argument('--cpus', type=int, default=2, help='Number of CPUs (default: 4)')
    parser.add_argument('--ios', type=int, default=2, help='Number of IO devices (default: 4)')
    
    args = parser.parse_args()
    
    return args
    

if __name__ == "__main__":

    args = parse_command_line_args()

    scheduling_algorithm = args.sched
    num_cpus = args.cpus
    num_ios = args.ios

    simulation = Scheduler(cores=num_cpus, io_devices=num_ios)

    try:
        simulation.readData(args.input)

        if scheduling_algorithm == "FCFS":
            simulation.FCFS()

    except FileNotFoundError as err:
        print(f"Simulation ERR: File could not be found... ")
    
    
    
    
    
    
    # """
    # This is how "rich" looks like its animated. The `Live` method keeps calling
    # the `generate_table()` function 40 times in this case with a small sleep in
    # between. I haven't experimented with the refresh_per_second value, so I don't know.
    # """
    # with Live(RenderScreen(new, ready, running, waiting, io, exited, random.randint(1, 50)), refresh_per_second=4) as live:
    #     live.update(RenderScreen(new, ready, running, waiting, io, exited, 1, s_time=random.randint(1, 50)))
    #     time.sleep(1)



    # b1 = [10, 16, 10, 17, 9, 15, 8, 15, 10, 15, 9, 15, 10, 17, 11, 15, 8, 17, 10]
    # b2 = [11, 16, 9, 16, 10, 15, 8, 16, 8, 17, 10, 15, 11, 17, 8, 17, 11, 16, 8]
    # b3 = [9, 16, 10, 15, 11, 16, 10, 16, 11, 15, 10, 15, 10, 17, 11, 16, 10]
    # b4 = [9, 16, 9, 15, 8, 15, 9, 15, 9, 16, 10, 15, 10, 16, 8, 17, 8, 16, 9, 17, 8, 16, 11]
    # p1 = PCB(0, "p2", b1, 0)
    # p2 = PCB(1, "p1", b2, 0)
    # p3 = PCB(2, "p3", b3, 1)
    # p4 = PCB(3, "p1", b4, 1)

    # new = [p3, p4]
    # ready = []
    # running = [p2]
    # waiting = []
    # io = [p1]
    # exited = []