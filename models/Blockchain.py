from models.Block import Block
from models.Txn import Txn
import json

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.unusedOP = {}
        self.pendingTxn = []
        self.currentTarget = None

    def newBlockchain(self):
        #return genesis block
        pass

    def addBlock(self, block):
        self.chain.append(block)

    def isTxnValid(self, txn):
        return txn.verifyTxn()

    def isBlockValid(self, block):
        pass

    def makePendingTxnJSON(self, JSONTxnList):
        TxnList = json.loads(JSONTxnList)
        for txnData in TxnList:
            txn = Txn()
            txn.makeTxnFromJSON(txnData)
            self.pendingTxn.append(txn)

    def getPendingTxnJSON(self):
        pendingTxnList = []
        for txn in self.pendingTxn:
            pendingTxnList.append(txn.getTxnJSON())

        return pendingTxnList
