from block import block
from uuid import uuid4
from txn import txn, output



class blockchain:
    
    

    def __init__(self):
        currTxn = txn("1")
        genesis = block(0, currTxn, 0x0)
        self.chain = [genesis]
        currTxn = None
        
    
    def mine(self, newBlock):
        target = 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        maxNonce = 2**32
        for i in range(maxNonce):
            if int(newBlock.hashf(), 16) <= target:
                self.chain.append(newBlock)
                break
            else:
                newBlock.nonce += 1

    
    def mineBlock(self):
        last = self.chain[-1]
        prevHash = last.hashf()
        newBlock = block((last.index+1), self.currTxn, prevHash)
        self.mine(newBlock)
        self.currTxn = None

  

    def newTrans(self,inp,rec,amt):
        self.currTxn = txn(inp)
        op = output(amt, rec)
        self.currTxn.outputs.append(op)

    @property
    def lastBlock(self):
        pass
        
        

blockchain = blockchain()
blockchain.newTrans(str(uuid4()),str(uuid4()),10)
blockchain.mineBlock()
for i in range(2):
    print(blockchain.chain[i].__dict__)
    print("\n")

