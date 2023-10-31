from datetime import datetime
import json
import time

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
    def __init__(self,pid,bursts,at):
        self.pid = pid     
        #self.priority = priority     # 0
        self.arrivalTime = at   
        self.totalBursts = len(bursts)
        self.bursts = bursts    #9 16  9 15  8 15  9 15  9 16  10 15  10 16  8 17  8 16  9 17  8 16  11
        self.currBurst = 'CPU'
        self.currBurstIndex = 0
        self.cpuBurst = int(bursts[0])
        self.ioBurst = int(bursts[1])
        self.readyQueueTime = 0
        self.runningQueueTime = 0
        self.waitQueueTime = 0
    
    def __repr__(self):
        return f"""pid: {self.pid}\ntotal bursts: {self.totalBursts}\ncurrent burst index: {self.currBurstIndex}
CPU Burst: {self.cpuBurst}\nIO Burst: {self.ioBurst}\nBursts: {self.bursts}\n\n"""

    def decrementCpuBurst(self):
        self.cpuBurst -= 1
        self.runningQueueTime += 1

    def decrementIoBurst(self):
        self.ioBurst -= 1
        self.waitQueueTime += 1
            
    def incrementBurstIndex(self):
        self.currBurstIndex += 1
    
    def getCurrentBurstTime(self):
        return int(self.bursts[self.currBurstIndex])


class CPU:
    '''
    Handles the life cycle of the simulation
    The CPU can run on either a FCFS first come first serve basis, or a Round Robin approach

    The simulated CPU has 4 cores by default but can be changed. 
    This will proportionally affect the 'processing power' of the simulated CPU.
    '''
    def __init__(self, cores:int=4):
        self.clock = SysClock()
        self.cores = cores
        self.num_processes = 0
        self.new = []
        self.ready = []
        self.running = []
        self.waiting = []
        self.exited = []

    def load_ready(self):
        '''
        if there exists processes in 'ready', and there are open slots in 'running'
            fill the 'running' queue up to the number of cores in the CPU.
        '''
        diff = self.cores - len(self.running)
        
        if diff > 0:
            while diff > 0 and self.ready:
                if len(self.ready) >= 1:
                    process = self.ready.pop(0)  # Remove the first process from the ready queue
                    self.running.append(process)
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
        for process in self.waiting:
            process.decrementIoBurst()

            if process.ioBurst == 0:
                process.incrementBurstIndex()
                process.cpuBurst = process.getCurrentBurstTime()
                self.ready.append(process)
                to_remove.append(process.pid)
                removed=True
    
        if removed: # rearrange the queues
            # remove any processes that were marked for removal.
            self.waiting = [x for x in self.waiting if x.pid not in to_remove]   
            

    def CPU_tick(self):
        '''
        handles a tick for the 'running' queue
        A single clock cycle for the CPU component
        '''
        to_remove = []
        removed = False

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
                
                to_remove.append(process.pid)
                removed=True
             
        if removed: # rearrange the queues
            # remove any processes that were marked for removal.
            self.running = [x for x in self.running if x.pid not in to_remove]   
            
            #   add the same number of PCB's removed from 'running', 
            #      from 'ready' into 'running'
            
            for i in range(len(to_remove)):
                if i + 1 < len(self.ready):
                    self.running.append(self.ready[i])
            
            # remove the old ones from ready seperately from where we add them.
            for i in range(len(to_remove)):
                if i + 1 < len(self.ready):
                    del self.ready[i]
    
    def readData(self, datfile):
        '''
        handles all .dat files produced for simulation.
        loads 'new' queue with new process control blocks (PCB) 
        using the format found in processes.dat and explained in the code below
        '''
        with open(datfile) as f:
            for process in f.read().split("\n"):
                if len(process) > 0:
                    parts = process.split(' ')
                    
                    arrival, pid = parts[0], parts[1]
                    priority, bursts = parts[2], parts[3:]

                    self.new.append(PCB(pid, bursts, arrival))

            self.num_processes += len(self.new)
        print(f"self.new\n{self.new}")


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
            
            # handles incrementing IO/CPU and shifting queues every clock tick. 
            self.load_ready()
            self.IO_tick()
            self.CPU_tick()
            # time.sleep(0.5)
            

            
            print(f"\n\n\nReady: {self.ready}")
            print(f"\n\n\nRunning: {self.running}")
            print(f"\n\n\nWaiting: {self.waiting}")
            print(f"\n\n\nExited: {self.exited}")
            print(f"total_processed: {self.total_processed}")

        print(f"total time: {self.clock.time() - start}")



if __name__=='__main__':
    sim = CPU(cores=1)
    sim.readData("processes.dat")
    sim.FCFS()
    print(sim)