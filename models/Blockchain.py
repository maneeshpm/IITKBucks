from models import Block, Txn

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.unusedOP = {}
        self.pendingTxn = []
        self.currentTarget = None

    def newBlockchain(self):
        #return genesis block
        pass

    def add_block(self, block):
        self.chain.append(block)

    def isTxnValid(self, txn):
        return txn.verifyTxn()

    def isBlockValid(self, block):
        pass

    def getPendingTxnJSON(self):
        pendingTxnList = []
        for txn in self.pendingTxn:
            pendingTxnList.append(txn.getTxnJSON())

        return pendingTxnList
