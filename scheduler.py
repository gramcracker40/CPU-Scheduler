from datetime import datetime
import json
import time
from sim import RenderScreen

class SysClock:
    def __init__(self):
        self.clock = 0
    
    def tick(self):
        self.clock += 1

    def time(self):
        return self.clock
    
class PCB:
    '''
    process control block
    '''
    def __init__(self,pid,priority,bursts,at):
        self.pid = pid     
        self.priority = priority     # 0
        self.arrivalTime = at   
        self.totalBursts = len(bursts)
        self.bursts = bursts    #9 16  9 15  8 15  9 15  9 16  10 15  10 16  8 17  8 16  9 17  8 16  11
        self.currBurst = 'CPU'
        self.currBurstIndex = 0
        self.cpuBurst = int(bursts[0])
        self.ioBurst = int(bursts[1])
        self.readyQueueTime = 0
        self.runningQueueTime = 0
        self.waitingQueueTime = 0
        self.ioQueueTime = 0
    
    def __repr__(self):
        return f"""\npid: {self.pid}\ntotal bursts: {self.totalBursts}\ncurrent burst index: {self.currBurstIndex}
CPU Burst: {self.cpuBurst}\nIO Burst: {self.ioBurst}\nBursts: {self.bursts}\nArrival Time: {self.arrivalTime}\n"""

    def decrementCpuBurst(self):
        self.cpuBurst -= 1
        self.runningQueueTime += 1

    def decrementIoBurst(self):
        self.ioBurst -= 1
        self.ioQueueTime += 1

    def incrementReadyTime(self):
        self.readyQueueTime += 1
    
    def incrementWaitingTime(self):
        self.waitingQueueTime += 1

    def incrementBurstIndex(self):
        self.currBurstIndex += 1
    
    def getCurrentBurstTime(self):
        return int(self.bursts[self.currBurstIndex])


class Scheduler:
    '''
    Handles the life cycle of the CPU scheduling simulation
    
    The CPU Scheduler can run on either a 
        FCFS first come first serve basis
        a Round Robin approach 
        or a priority based approach

    The simulated CPU has 2 cores by default but can be changed. 
    the number of cores is the allowed number of processes in the running queue at once. 
    
    Specify the number of io devices to allow in the IO queue 
    and be decremented by 1 on their ioBurst every clock tick

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
        
        self.new = []
        self.ready = []
        self.running = []
        self.waiting = []
        self.IO = []
        self.exited = []


    def load_new(self, clock_tick:int):
        '''
        load the new queue according to the current clock tick.
        '''
        if clock_tick in self.pcb_arrivals:
            for pcb in self.pcb_arrivals[clock_tick]:
                self.new.append(pcb)
    
    def load_ready(self):
        '''
        if there exists processes in 'ready', and there are open slots in 'running'
            fill the 'running' queue up to the number of available 'cores' in the CPU.
        '''
        diff = self.cores - len(self.running)

        for process in self.ready:
            process.incrementReadyTime()
        
        if diff > 0:
            while diff > 0 and self.ready:
                if len(self.ready) >= 1:
                    process = self.ready.pop(0)  # Remove the first process from the ready queue
                    self.running.append(process)
                diff -= 1

    
    def load_waiting(self):
        '''
        loads the PCBs that are in the 'waiting' queue in to the 'IO' queue based on the number
            of io devices there are available for the 'IO' queue. 
            
            Also increments the waiting time of each of the processes inside of waiting. 
        '''
        diff = self.io_devices - len(self.IO)

        for process in self.waiting:
            process.incrementWaitingTime()

        if diff > 0:
            while diff > 0 and self.waiting:       # if there is a difference
                if len(self.waiting) >= 1:         # if there are any waiting
                    process = self.waiting.pop(0)  # Remove the first process from the waiting queue
                    self.IO.append(process)        # add the process to the IO queue
                diff -= 1


                    
    def IO_tick(self):
        '''
        tick all processes in IO bounds bursts by 1
        first see if the PCB is on its last burst, if it is then 
        send it from 'waiting' to 'exited'. PCB's end on CPU burst
        
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
            

    def FCFS_CPU_tick(self):
        '''
        handles a single decrement of cpuBurst for the 'running' queue while running FCFS
        A single clock cycle for the CPU component. Determines if processes
        need to be placed in waiting for their next ioBurst, or if they need
        to be placed in exited because they are done processing. 


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
                    self.exited.append(process)
                    self.total_processed += 1
                    
                removed.append(process.pid)
             
        if removed: # rearrange the queues
                    # remove any processes from 'running' that were marked for removal.
            self.running = [x for x in self.running if x.pid not in removed]   

    
    def readData(self, datfile):
        '''
        handles all .dat files produced for simulation.
        loads 'new' queue with new process control blocks (PCB) 
        using the format found in processes.dat and explained in the code below
        '''
        with open(datfile) as f:
            for process in f.read().split("\n"):
                if len(process) > 0:
                    self.num_processes += 1
                    parts = process.split(' ')
                    
                    arrival, pid = parts[0], parts[1]
                    priority, bursts = parts[2], parts[3:]

                    if arrival in self.pcb_arrivals:
                        self.pcb_arrivals[arrival].append(PCB(pid, priority, bursts, arrival))
                    else:
                        self.pcb_arrivals[arrival] = [PCB(pid, priority, bursts, arrival)]
    
        print(f"self.pcb_arrivals\n{self.pcb_arrivals}")


    def FCFS(self):
        '''
        does a first come first serve algorithm on the CPU's 'new' processes
        sorts based off of the processes arrival time. 
        does not switch until the cpu burst is complete. 
        running state holds number of cores set in __init__
        '''
        total_processes = len(self.new)
        # set the new processes to the ready queue. 
        self.new.sort(key=lambda x: x.arrivalTime)
        self.ready = self.new
        self.new = []

        print(f"Ready: {self.ready}")
        # set the number of running processes to the number of cores available. 
        self.running = self.ready[:self.cores]
        self.ready = self.ready[self.cores:]

        print(f"Ready: {self.ready}")
        print(f"Running: {self.running}")
        
        self.total_processed = 0
        start = self.clock.time()
        
        while self.total_processed + 1 <= total_processes:  
            self.clock.tick()
            # decrements the cpuBurst of the PCBs in 'running' by 1
            # uses a fcfs rule set to determine how to run the PCBs
            self.FCFS_CPU_tick()
            # loads PCBs from 'ready' into 'running' based off the number of 'cores'
            self.load_ready()
            # decrements the ioBurst of the PCBs in 'IO' by 1
            self.IO_tick()
            # loads PCBs from 'waiting' into 'IO' based off the number of 'io_devices'
            self.load_waiting()
  
            # time.sleep(0.5)

            RenderScreen(self.new, self.ready, self.running, self.waiting, self.IO, self.exited, 1)
            
            # print(f"\n\n\nReady: {self.ready}")
            # print(f"\n\n\nRunning: {self.running}")
            # print(f"\n\n\nWaiting: {self.waiting}")
            # print(f"\n\n\nIO: {self.IO}")
            # print(f"\n\n\nExited: {self.exited}")
            # print(f"total_processed: {self.total_processed}")

        print(f"total time: {self.clock.time() - start}")



if __name__=='__main__':
    scheduler = Scheduler(cores=1, io_devices=1)
    scheduler.readData("processes.dat")
    scheduler.FCFS()
