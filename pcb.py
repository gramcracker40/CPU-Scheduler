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

