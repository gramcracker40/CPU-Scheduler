from datetime import datetime
import json
import time
from rich.live import Live
from sim_viewer import RenderScreen
from sim_viewer import RenderStats
from pcb import PCB, SysClock

class Scheduler:
    '''
    Handles the life cycle of the CPU scheduling simulation

    
    The CPU Scheduler can run on either a 
        FCFS first come first serve basis
        a Round Robin approach 
        or a priority based approach

        see schedule() for more info on scheduling algorithms

    The simulated CPU has 2 cores by default but can be changed. 
    the number of cores is the allowed number of processes in the running queue at once. 
    
    The simulated runtime environment only has 2 'io_devices' by default but can also be changed., 
    this handles input/output between calculations between CPU bursts
    
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
        self.highest_priority = 10000
        
        self.new = []
        self.ready = []
        self.running = []
        self.waiting = []
        self.IO = []
        self.exited = []

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
                    priority, bursts = int(parts[2][1]), [int(i) for i in parts[3:]]

                    if arrival in self.pcb_arrivals:
                        self.pcb_arrivals[arrival].append(PCB(pid, priority, bursts, arrival))
                    else:
                        self.pcb_arrivals[arrival] = [PCB(pid, priority, bursts, arrival)]
    
    def get_total_new_processes(self):
        '''
        helper func
        grabs number of total processes in self.pcb_arrivals for scheduling type to process.
        '''
        return len([each for x in self.pcb_arrivals for each in self.pcb_arrivals[x]])
    
    def update_messages(self, message:str, tick:int, style="green"):
        '''
        helper func
        pass a message to add to messages
        pass the Live object from Rich app so the update can occur.
        '''
        self.messages.insert(0, {"message": message, "style": style})

    def new_to_ready(self):
        '''
        helper func
        '''
        for _ in range(len(self.new)):
            self.ready.append(self.new.pop(0))

    def find_highest_priority(self, queue):
        '''
        helper func
        return index of PCB inside of queue with the highest priority
        '''
        highest_priority = (self.highest_priority, -1)
        for count, p in enumerate(queue):
            if p.priority < highest_priority[0]:
                highest_priority = [p.priority, count]
        return highest_priority[1]
    
    def check_slice_tracker(self, clock_tick:int, time_slice:int):
        '''
        for Round Robin scheduling. 

        handles all Round Robin functionality in schedule()
        
        checks all active slices created by load_waiting() and load_ready()
        
        removes PCBs from 'running' and 'io' if they have been in the queue
        for the given round robin time slice. 
        '''
        to_remove = []
        for process in self.time_slice_tracker:
            # time entered and the queue name the pcb entered into. Either
            t_entered = self.time_slice_tracker[process][0]
            queue = self.time_slice_tracker[process][1]

            # time to switch PCB receiving resources 
            if t_entered + time_slice <= clock_tick: 
                temp = -1
                if queue == "io":
                    # find the process PCB object in IO.
                    for each in self.IO:
                        if each.pid == process:
                            temp = each
                    if temp == -1: # the process was removed mid IO burst
                        break      # break out, the process has already been handled.
                    # remove the process from IO and add to waiting
                    self.IO = [p for p in self.IO if p.pid != temp.pid]
                    self.waiting.append(temp)
                else: # running
                    # find the process PCB object in running.
                    for each in self.running:
                        if each.pid == process:
                            temp = each
                    if temp == -1: # the process was removed mid CPU burst
                        break 
                    # remove the PCB from running and add to ready. 
                    self.running = [p for p in self.running if p.pid != temp.pid]
                    self.ready.append(temp)
                # mark the process for removal from time_slice_tracker
                to_remove.append(process)
                
        # remove any non active slice tracking objects.
        if to_remove:
            for p in to_remove:
                del self.time_slice_tracker[p]


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
                    self.time_slice_tracker[process.pid] = (clock_tick, "running")
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
            if len(self.waiting) >= 1:         # if there are any waiting, assign them immediately based off 'mode'
                if mode == "FCFS":
                    process = self.waiting.pop(0)
                elif mode == "PB":
                    process = self.waiting.pop(self.find_highest_priority(self.waiting))
                elif mode == "RR":
                    process = self.waiting.pop(0)
                    self.time_slice_tracker[process.pid] = (clock_tick, "io")
                # update the message section
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

                    process.queueTime = (process.readyQueueTime + process.runningQueueTime \
                            + process.waitingQueueTime + process.ioQueueTime) - 1

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

        Available scheduling algorithms --> \n
            # 'FCFS' - First come first serve
            # 'RR' - Round Robin, you can also change the 'time_slice'
            # 'PB' - Priority Based, scheduled based off of highest priority. 

            will also show the simulation of the running processes in the various
            queues using the various methods in __name__ == '__main__'. 
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
                    self.load_waiting(tick)
                elif mode == "PB":
                    self.load_ready(tick, mode="PB")
                    self.load_waiting(tick, mode="PB")
                elif mode == "RR":
                    self.check_slice_tracker(tick, time_slice)
                    self.load_ready(tick, mode="RR")
                    self.load_waiting(tick, mode="RR")

                self.CPU_tick(tick)
                self.IO_tick()
                    

                time.sleep(.0001)

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
    # scheduler.schedule(mode="FCFS")
    scheduler.schedule(mode="PB")
    # scheduler.schedule(mode="RR", time_slice=4)
