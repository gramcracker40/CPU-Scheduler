from datetime import datetime
import json
import time
from rich.live import Live
from sim_viewer import RenderScreen
from sim_viewer import RenderStats
from pcb import PCB

# from sim import RenderScreen

class SysClock:
    def __init__(self):
        self.clock = 0
    
    def tick(self):
        self.clock += 1

    def time(self):
        return self.clock
    

class Scheduler:
    '''
    Handles the life cycle of the CPU scheduling simulation
    
    The CPU Scheduler can run on either a 
        FCFS first come first serve basis
        a Round Robin approach 
        or a priority based approach

    The simulated CPU has 2 cores by default but can be changed. 
    the number of cores is the allowed number of processes in the running queue at once. 
    
    The simulated runtime environment only has 2 'io_devices' at a tim, 
        this handles input/output between calculations in the CPU

    self.new --> the 'new' processes, based off the PCB's arrival time.
    self.ready --> the 'ready' processes, added by load_ready according to the number of cores
    
    '''
    def __init__(self, cores:int=2, io_devices:int=2):
        self.clock = SysClock()
        
        self.cores = cores
        self.io_devices = io_devices

        self.num_processes = 0
        self.process_turnover_time = 0
        self.pcb_arrivals = {}
        self.messages = []
        self.time_slice_tracker = {}
        
        self.new = []
        self.ready = []
        self.running = []
        self.waiting = []
        self.IO = []
        self.exited = []

    def get_total_new_processes(self):
        '''
        grabs number of total processes in self.pcb_arrivals for scheduling type to process.
        '''
        return len([each for x in self.pcb_arrivals for each in self.pcb_arrivals[x]])
    
    
    def readData(self, datfile):
        '''
        handles all .dat files produced for simulation.
        loads 'pcb_arrivals' queue with new process control blocks (PCB)
        using the format found in processes.dat and explained in the code below

        pcb_arrivals: format --> {0: [<PID obj-1>], 1: [<PID obj-2>, <PID obj-3>], 3: [<PID obj-4>]}
        '''
        with open(datfile) as f:
            for process in f.read().split("\n"):
                if len(process) > 0:
                    self.num_processes += 1
                    parts = process.split(' ')
                    
                    arrival, pid = int(parts[0]), parts[1]
                    priority, bursts = int(parts[2][1]), parts[3:]

                    print(f"Arrival ::: Type {type(arrival)}")
                    bursts = [int(i) for i in bursts]

                    if arrival in self.pcb_arrivals:
                        self.pcb_arrivals[arrival].append(PCB(pid, priority, bursts, arrival))
                    else:
                        self.pcb_arrivals[arrival] = [PCB(pid, priority, bursts, arrival)]
    
        print(f"self.pcb_arrivals\n{self.pcb_arrivals}\n{self.pcb_arrivals[0]}")
    
    def update_messages(self, message:str, tick:int, style="green"):
        '''
        pass a message to add to messages
        pass the Live object from Rich app so the update can occur.
        '''
        self.messages.insert(0, {"message": message, "style": style})
        
    def load_new(self, clock_tick:int):
        '''
        load the new queue with PCBs according to the current clock tick.
        '''
        try:
            self.new = [pcb for pcb in self.pcb_arrivals[clock_tick] 
                        if clock_tick in self.pcb_arrivals]
            for new in self.new: # display the messages associated with the loading of the PCBs
                self.update_messages(
                    f"{clock_tick}, job {new.pid} entered the 'new' queue", clock_tick
                )
        except KeyError:
            pass
        #print(self.new)

    def new_to_ready(self):
        '''
        TODO: helper func
        '''
        for _ in range(len(self.new)):
            self.ready.append(self.new.pop(0))

    def find_highest_priority(self, queue):
        '''
        TODO: helper func
        return index of PCB with highest priority
        '''
        highest_priority = -1
        for count, p in enumerate(self.ready):
            if p.priority > highest_priority:
                highest_priority = count
        return highest_priority
    
    def load_ready(self, clock_tick:int, mode:str="FCFS"):
        '''
        ## loads PCBs from 'new' into 'ready' immediately.
        ## loads PCBs from 'ready' into 'running' based off the number of 'cores'
        
        chooses PCBs to send to 'running' off of a first come first serve approach by default.
        can run in 'priority based' 'PB' mode as well for choosing which PCB's load into 'running' from 'ready'.

        ## if there exists processes in 'ready', and there are open slots in 'running'
        ## fill the 'running' queue up to the number of available 'cores' in the CPU.
        '''

        # load the PCB from 'new' into 'ready'
        self.new_to_ready()
        
        # determine the difference between lengths of 'running' and the available 'cores'
        diff = self.cores - len(self.running)

        # if there exists available cpu 'cores', assign the ready processes immediately to 'running. 
        while diff > 0 and self.ready:
            if len(self.ready) >= 1:
                if mode == "FCFS":
                    process = self.ready.pop(0)
                elif mode == "PB":
                    process = self.ready.pop(self.find_highest_priority(self.ready))
                elif mode == "RR":
                    process = self.ready.pop(0)
                    self.time_slice_tracker[process.pid] = clock_tick
                self.update_messages(
                    f"{clock_tick}, job {process.pid}, priority {process.priority} began running {process.cpuBurst} CPU bursts, burst: {process.currBurstIndex}/{process.totalBursts}", 
                    clock_tick, style="cyan"
                )
                self.running.append(process)
                
            diff -= 1

        # increment the time in ready by one if they are staying in ready.
        for process in self.ready:
            process.incrementReadyTime()

    def load_waiting(self, clock_tick:int, mode:str="FCFS"):
        '''
        # loads PCBs from 'waiting' into 'IO' based off the number of 'io_devices' 
        # increments the waiting time of each of the processes inside of waiting. 
        '''
        diff = self.io_devices - len(self.IO)

        while diff > 0 and self.waiting:       # if there is a difference
            if len(self.waiting) >= 1:         # if there are any waiting
                if mode == "FCFS":
                    process = self.waiting.pop(0)
                elif mode == "PB":
                    process = self.waiting.pop(self.find_highest_priority(self.waiting))
                self.update_messages(
                    f"{clock_tick}, job {process.pid} began running {process.ioBurst} IO bursts, {process.currBurstIndex}/{process.totalBursts}", 
                    clock_tick, style="bright_magenta"
                )
                self.IO.append(process)        # add the process to the IO queue
            diff -= 1

        for process in self.waiting:
            process.incrementWaitingTime()

    def IO_tick(self):
        '''
        # decrements the ioBurst of the PCBs in 'IO' by 1

        sends PCBs to 'ready' whenever they are done processing, can be changed
            to allow for slicing or even priority based loading from 'waiting'
        
        decrement 1 from the waiting queue and see if any are done. 
        If they are done move from 'waiting' to 'ready'
        '''
        to_remove = []
        removed = False
        for process in self.IO:
            process.decrementIoBurst()

            if process.ioBurst == 0:
                process.incrementBurstIndex()
                process.cpuBurst = process.getCurrentBurstTime()
                self.ready.append(process)
                to_remove.append(process.pid)
                removed=True
    
        if removed: # rearrange the queues
            # remove any processes that were marked for removal.
            self.IO = [x for x in self.IO if x.pid not in to_remove]   
            

    def CPU_tick(self, clock_tick:int):
        '''
        ### decrements the cpuBurst of the PCBs in 'running' by 1
        ### A single clock cycle for the CPU component. 
        
        Determines if processes need to be placed in waiting for their next ioBurst, 
        or if they need
        to be placed in exited because they are completely done processing. 


        '''
        removed = []

        for process in self.running:
            process.decrementCpuBurst()

            if process.cpuBurst == 0:
                process.incrementBurstIndex()
                # if its not the last burst
                if process.currBurstIndex != process.totalBursts:
                    process.ioBurst = process.getCurrentBurstTime()
                    self.waiting.append(process)
                else: # if it is the last burst
                    process.processTime = clock_tick - process.arrivalTime

                    process.queueTime = process.readyQueueTime + process.runningQueueTime \
                            + process.waitingQueueTime + process.ioQueueTime

                    self.update_messages(
                        f"{clock_tick}, job {process.pid} exited. Total completion time --> {process.processTime} --> Queue Time: {process.queueTime}",
                        clock_tick, style="red"
                    )
                    process.timeExited = clock_tick
                    self.exited.append(process)
                    self.total_processed += 1
                    
                removed.append(process.pid)
             
        if removed: # rearrange the queues
                    # remove any processes from 'running' that were marked for removal.
            self.running = [x for x in self.running if x.pid not in removed] 

    def schedule(self, mode:str="FCFS", time_slice:int=10):
        '''
        Given a mode and loaded PCBs from readData use one of the available
            scheduling algorithms to process the PCBs to completion. 

            will also show the simulation of the running processes in the various
            queue using the various methods. 
        ''' 
        total_processes = self.get_total_new_processes()

        self.total_processed = 0
        start = self.clock.time()

        # Run the FCFS scheduling algorithm while showing a graphical representation.
        with Live(RenderScreen(self.new, self.ready, self.running, self.waiting, self.IO, 
                               self.exited, 0, self.messages), refresh_per_second=10) as live:
            while self.total_processed < total_processes:  
            # load the PCB's into new queue based off of the clock time
                tick = self.clock.time()
                self.load_new(tick)
                if mode == "FCFS":
                    self.load_ready(tick)
                elif mode == "PB":
                    self.load_ready(tick, mode="PB")
                
                self.CPU_tick(tick) 

                if mode == "FCFS":
                    self.load_waiting(tick)
                elif mode == "PB":
                    self.load_waiting(tick, mode="PB")
                
                self.IO_tick()
            
                time.sleep(0.01)

                self.clock.tick()
                # update the simulation.
                live.update(RenderScreen(self.new, self.ready, self.running, 
                                         self.waiting, self.IO, self.exited, tick, self.messages))
        
        end = self.clock.time()
        print(f"total time: {(end - start) - 1}")
        RenderStats(self.exited)

    def FCFS(self):
        '''
        does a first come first serve algorithm on the CPU's 'new' processes
        does not switch until the cpu burst is complete. 
        running state holds number of cores set in __init__
        '''
        total_processes = self.get_total_new_processes()

        self.total_processed = 0
        start = self.clock.time()

        
        # Run the FCFS scheduling algorithm while showing a graphical representation.
        with Live(RenderScreen(self.new, self.ready, self.running, self.waiting, self.IO, 
                               self.exited, 0, self.messages), refresh_per_second=10) as live:
            while self.total_processed < total_processes:  
            # load the PCB's into new queue based off of the clock time
                tick = self.clock.time()
                self.load_new(tick)
                self.load_ready(tick)
                self.load_waiting(tick)
                self.CPU_tick(tick) 
                self.IO_tick()
            
                time.sleep(0.01)

                self.clock.tick()
                # update the simulation.
                live.update(RenderScreen(self.new, self.ready, self.running, 
                                         self.waiting, self.IO, self.exited, tick, self.messages))
        
        end = self.clock.time()
        print(f"total time: {(end - start) - 1}")
        RenderStats(self.exited)

    def PB(self):
        '''
        Priority Based
        Runs the sheduler with the loaded processes in a priority based fashion. 
        
        The higher the processes priority, the more preference it has in being chosen to 
        go into the 'running' or 'IO' queues from the 'ready' and 'waiting' queues. 
        
        Shows that a priority based approach could be better for handling background noise
        and allowing a user to navigate the computer more efficiently.
        '''
        total_processes = self.get_total_new_processes()

        self.total_processed = 0
        start = self.clock.time()

        # Run the FCFS scheduling algorithm while showing a graphical representation.
        with Live(RenderScreen(self.new, self.ready, self.running, self.waiting, self.IO, 
                               self.exited, 0, self.messages), refresh_per_second=10) as live:
            while self.total_processed < total_processes:  
            # load the PCB's into new queue based off of the clock time
                tick = self.clock.time()
                self.load_new(tick)
                self.CPU_tick(tick) 
                self.load_ready(tick, mode="PB")
                self.IO_tick()
                self.load_waiting(tick, mode="PB")
            
                time.sleep(0.01)

                self.clock.tick()
                # update the simulation.
                live.update(RenderScreen(self.new, self.ready, self.running, 
                                         self.waiting, self.IO, self.exited, tick, self.messages))

        end = self.clock.time()
        print(f"total time: {(end - start) - 1}")
        RenderStats(self.exited)

if __name__=='__main__':
    scheduler = Scheduler(cores=1, io_devices=4)
    scheduler.readData("processes.dat")
    scheduler.FCFS()
