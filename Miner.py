from threading import Thread, Event
import time
import requests

class Miner(Thread):
    def __init__(self, blockchain, out_q):
        super().__init__()
        self.blockchain = blockchain
        self.mineHandler = Event()
        self.out_q = out_q
        self.block = None
    
    def postMiningSteps(self, block):
        self.blockchain.addBlock(block)
        self.propagateBlock(block)

    def propagateBlock(self,block):
        data = block.toByteArray()
        index = block.index
        for peer in self.blockchain.peers:
            req = requests.post(
                url=peer+'/newBlock',
                data=data,
                headers={'Content-Type': 'application/octet-stream'}
                )
            if req.status_code == 200:
                print(f"[SUCCESS] Block {index} sent to {peer}")
            else:
                print(f"[WARNING] Peer {peer} responded {req.status_code}")     

    
    def run(self):
        while not len(self.blockchain.pendingTxn) > 0:
            time.sleep(1)

        block = self.blockchain.getBlockToMine(myPubKey)
        i = 0
        while not self.mineHandler().isSet():
            block.nonce = i
            block.timeStamp = time.perf_counter_ns()
            if int.from_bytes(block.getHeaderHash(),'big') <= block.target:
                self.out_q.put(block)
                self.block = block
                self.postMiningSteps(block)
                break

        if self.out_q.empty():
            print("interrupted")
        

    def join(self):
        self.mineHandler.set()
        super().join()
