from threading import Thread, Event
import time

class Miner(Thread):
    def __init__(self, blockchain, out_q):
        super().__init__()
        self.blockchain = blockchain
        self.mineHandler = Event()
        self.out_q = out_q
        self.block = None
    
    def run(self):
        block = self.blockchain.getBlockToMine()
        i = 0
        while not self.mineHandler().isSet():
            block.nonce = i
            block.timeStamp = time.perf_counter_ns()
            if int.from_bytes(block.getHeaderHash(),'big') <= block.target:
                self.out_q.put(block)
                self.block = block
                self.postMiningSteps()
                break

        if self.out_q.empty():
            print("interrupted")
        
    def postMiningSteps(self):
        print(self.block)

    def join(self):
        self.mineHandler.set()
        super().join()
