class PCB:
    '''
    process control block
    '''
    def __init__(self,pid:int,priority:int,bursts:list,at:int):
        self.pid = pid     
        self.priority = priority     # 0
        self.arrivalTime = at   
        self.totalBursts = len(bursts)
        self.bursts = bursts    #9 16  9 15  8 15  9 15  9 16  10 15  10 16  8 17  8 16  9 17  8 16  11
        self.totalBurstTime = sum(self.bursts)
        self.processTime = 0
        self.remainingBurst = self.totalBurstTime
        self.currBurst = 'CPU'
        self.currBurstIndex = 0
        self.cpuBurst = bursts[0]
        self.ioBurst = bursts[1]
        self.readyQueueTime = 0
        self.runningQueueTime = 0
        self.waitingQueueTime = 0
        self.ioQueueTime = 0
        self.queueTime = 0
        #need a var for tracking when the pcb enters the exit que
        self.timeExited = 0
    
    def __repr__(self):
        return f"""\npid: {self.pid}\ntotal bursts: {self.totalBursts}\ncurrent burst index: {self.currBurstIndex}
CPU Burst: {self.cpuBurst}\nIO Burst: {self.ioBurst}\nBursts: {self.bursts}\nArrival Time: {self.arrivalTime}
Remaining Burst Time: {self.remainingBurst}"""

    def decrementCpuBurst(self):
        self.cpuBurst -= 1
        self.runningQueueTime += 1
        self.remainingBurst -= 1

    def decrementIoBurst(self):
        self.ioBurst -= 1
        self.ioQueueTime += 1
        self.remainingBurst -= 1

    def incrementReadyTime(self):
        self.readyQueueTime += 1
    
    def incrementWaitingTime(self):
        self.waitingQueueTime += 1

    def incrementBurstIndex(self):
        self.currBurstIndex += 1
    
    def getCurrentBurstTime(self):
        return int(self.bursts[self.currBurstIndex])


class SysClock:
    def __init__(self):
        self.clock = 0
    
    def tick(self):
        self.clock += 1

    def time(self):
        return self.clock
    