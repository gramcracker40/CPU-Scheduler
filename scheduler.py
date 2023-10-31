from datetime import datetime
import json

class SysClock:
    def __init__(self):
        self.__dict__ = self._shared_state
        if not 'clock' in self.__dict__: 
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
        self.cpuBurst = bursts[0]
        self.readyQueueTime = 0
        self.runningQueueTime = 0
        self.waitQueueTime = 0
        self.cpuTime = 0

    def decrementCpuBurst(self):
        self.bursts[self.currBurstIndex] -= 1
        self.runningQueueTime += 1

    def decrementIoBurst(self):
        self.bursts[self.currBurstIndex] -= 1
        self.waitQueueTime += 1

    def incrementBurstIndex(self):
        self.currBurstIndex += 1
    
    def getCurrentBurstTime(self):
        return self.bursts[self.currBurstIndex]


class CPU:
    '''
    Handles the life cycle of the simulation
    The CPU can run on either a FCFS first come first serve basis, or a Round Robin approach

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


    def FCFS(self):
        '''
        does a first come first serve algorithm on the CPU's 'new' processes
        sorts based off of the processes arrival time. 
        does not switch until the cpu burst is complete. 
        ready state holds number of cores set in __init__
        '''
        total_processes = len(self.new)
        # set the new processes to the ready queue. 
        self.ready = self.new.sort(key=lambda x: x.arrivalTime)

        # set the number of running process to the number of cores available. 
        self.running = self.ready[:self.cores]
        self.ready = self.ready[self.cores:]

        total_processed = 0
        while total_processed < total_processes:
            self.clock.tick()
            
            # incase we need to remove a process from 'running' in this clock tick
            to_remove = []
            # handle updates of the status of running processes
            for process in self.running:
                process.decrementCpuBurst()

                # remove the process from 'running', add to 'waiting' increment burst index
                if process.cpuBurst == 0:
                    process.incrementBurstIndex()
                    self.processes["waiting"].append(process)
                    to_remove.append(process.pid)
                
            self.running


            
            


    def readData(self, datfile):
        '''
        handles all .dat files produced for simulation.
        loads 'new' queue with new process control blocks (PCB) 
        '''
        with open(datfile) as f:
            for process in f.read().split("\n"):
                if len(process) > 0:
                    parts = process.split(' ')
                    arrival = parts[0]
                    pid = parts[1]
                    priority = parts[2]
                    bursts = parts[3:]

                    self.new.append(PCB(pid, bursts, arrival))

                    print(f"self.new\n\n{self.processes['new']}")

                    print(f"{arrival}, {pid}, {priority} {len(bursts)}{bursts}\n")
            self.num_processes += len(self.processes['new'])



if __name__=='__main__':
    sim = CPU(1, "processes.dat")
    print(sim)