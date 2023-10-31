from datetime import datetime

class PCB:
    '''
    process control block
    '''
    def __init__(self,pid,bursts,at):
        self.pid = pid     
        #self.priority = priority     # 0
        self.arrivalTime = at
        self.bursts = bursts    # 5 3  2 2  2 3  3 3 3 2 3 3 4 2 5 2 5 3 3 3 4
        self.currBurst = 'IO'
        self.currBurstIndex = 1
        self.cpuBurst = 5
        self.readyQueueTime = 0
        self.waitQueueTime = 0
        self.cpuTime = 0

    def decrementCpuBurst(self):
        self.bursts[self.currBurstIndex] -= 1

    def decrementIoBurst(self):
        self.bursts[self.currBurstIndex] -= 1

    def incrementBurstIndex(self):
        self.currBurstIndex += 1
    
    def getCurrentBurstTime(self):
        return self.bursts[self.currBurstIndex]


class CPU:
    '''
    Handles the life cycle of the simulation
    '''
    def __init__(self, cores=4):
        self.processes = {
            'new': [],
            'ready': [],
            'running': [],
            'waiting': [],
            'exited': [],
        }


    def __str__(self):
        s = ""
        s += "datfile: "+self.datfile +"\n"
        s += "new queue: "+",".join(self.new)  +"\n"
        s += "wait: "+",".join(self.wait)  +"\n"
        return s


    def readData(self):
        '''
        handles all .dat files produced for simulation.
        loads 'new' queue with new process control blocks (PCB) 
        '''
        with open(self.datfile) as f:
            for process in f.read().split("\n"):
                if len(process) > 0:
                    parts = process.split(' ')
                    arrival = parts[0]
                    pid = parts[1]
                    priority = parts[2]
                    bursts = parts[3:]

                    self.processes['new'].append(PCB(pid, bursts, arrival))

                    print(f"{arrival}, {pid}, {priority} {len(bursts)}{bursts}\n")



class CPUScheduler:
    '''
    Handles scheduling of CPU components
    '''

    def __init__(self):
        '''
        Initialize a CPU Scheduler.
        '''

    