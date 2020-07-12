from models.Block import Block
from models.Txn import Txn
from models.Output import Output
import json
import hashlib
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
import requests
import time

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.unusedOP = {}
        self.unusedOPMap = {}
        self.pendingTxn = {}
        self.currentTarget = None
        self.numBlocks = 0

    def addBlock(self, block):
        self.processBlock(block)
        self.chain.append(block.getHeaderHash())
        self.numBlocks += 1
        block.export()

    def isTxnPending(self, txn):
        if txn.getTxnHash() in self.pendingTxn.keys():
            return True
        return False

    def isTxnValid(self, txn):
        if not self.isTxnPending(txn.getTxnHash()):
            return False
        opHash = txn.getOutputHash()
        sumInputs = 0
        for inp in txn.totInput:
            if (inp.txnID, inp.opIndex) not in self.unusedOP.keys():
                return False
            
            verifier = PKCS1_PSS.new(self.unusedOP[(inp.txnID, inp.opIndex)].pubKey)
            h = SHA256.new(inp.TxnID + int.to_bytes(inp.opIndex) + opHash)
            if not verifier.verify(h, inp.sign):
                return False
            sumInputs += self.unusedOP[(inp.txnID, inp.opIndex)].noCoins
        sumOutputs = txn.getOutputCoins()
        return sumOutputs <= sumInputs, sumInputs-sumOutputs

    def getParentBlockHashTime(self, index):
        if index == -1:
            with open('blockchain/blocks/'+str(0),'rb') as genesisblock:
                return bytes.fromhex('0'*64), int.from_bytes(genesisblock[100:108], 'big')
        with open('blockchain/blocks/'+str(index),'rb') as blockByteArrar:
            return hashlib.sha256(blockByteArrar[:116]).digest(), int.from_bytes(blockByteArrar[100:108], 'big')

    def isBlockValid(self, block):
        if block.index != self.numBlocks:
            return False
        parHash, parTime = self.getParentBlockHashTime(self.numBlocks)
        if parTime > block.timeStamp:
            return False
        if block.parentHash != parHash:
            return False
        if block.target != self.currentTarget:
            return False
        if block.getHeaderHash() > self.currentTarget:
            return False
        
        totalReward = 0
        for i in range(len(block.txns)):
            if i==0: 
                continue
            valid, reward = self.isTxnValid(block.txns[i])
            if not valid:
                return False
            totalReward += reward
        return totalReward >= block.txns[0].getOutputCoins()

    def makePendingTxnJSON(self, JSONTxnList):
        TxnList = json.loads(JSONTxnList)
        for txnData in TxnList:
            txn = Txn()
            txn.makeTxnFromJSON(txnData)
            self.addPendingTxn(txn)
    
    def addPendingTxn(self, txn):
        self.pendingTxn[txn.getTxnHash()] = txn
    
    def removeOPFromUnusedOPMap(self, op):
        try:
            del self.unusedOPMap[op.pubKey][op.getOPHash()]
        except:
            print("Output does not exist")

    def addOPToUnusedOPMap(self, op):
        if op.pubKey in self.unusedOPMap:
            self.unusedOPMap[op.pubKey][op.getOPHash()] = op
        else:
            self.unusedOPMap[op.pubKey] = {}
            self.unusedOPMap[op.pubKey][op.getOPHash()] = op        
        self.unusedOPMap[op.pubKey][op.getOPHash()] = op
    
    def processBlock(self, block):
        for txn in block.txns:
            del self.pendingTxn[txn.getTxnHash()]

            for inp in txn.totInputs:
                op = self.unusedOP[(inp.txnID, inp.opIndex)]
                del self.unusedOP[(inp.txnID, inp.opIndex)]
                self.removeOPFromUnusedOPMap(op)
            for i in range(len(txn.totOutputs)):
                self.unusedOP[(txn.id, i)] = txn.totOutputs[i]
                self.addOPToUnusedOPMap(op)

    def getPendingTxnJSON(self):
        pendingTxnList = []
        for txn in self.pendingTxn:
            pendingTxnList.append(txn.getTxnJSON())

        return pendingTxnList

    def buildBlockchain(self, peer):
        peerGetBlockURL = peer + '/getBlock/'
        i = 0
        while True:
            r = requests.get(url = peerGetBlockURL + str(i))
            if r.status_code != 200:
                break
            block = Block()
            block.blockFromByteArray(r.content)
            if self.isBlockValid(block):
                self.addBlock(block)
            else:
                return print("Invalid Block")

    def buildPendingTxns(self, peer):
        peerGetPendingTxnURL = peer+ '/getPendingTransactions'
        r = requests.get(url = peerGetPendingTxnURL)
        self.makePendingTxnJSON(r.json)
    
    def initializeBlockchain(self, genesis, myNode):
        potentialPeers = [genesis]
        peers = []
        myUrl = {"url":myNode}
        for potentialPeer in potentialPeers:
            if len(peers)>=5:
                break
            r = requests.post(url=potentialPeer+"/newPeer", json=myUrl)
            if r.status_code == 200:
                peers.append(potentialPeer)
                potentialPeers.remove(potentialPeer)
            else:
                r = requests.get(url = potentialPeer+"/getPeers")
                externalPeers = r.json()["peers"]
                for externalPeer in externalPeers:
                    if externalPeer not in potentialPeers:
                        potentialPeers.append(externalPeer)
        
        self.buildBlockchain(peers[0])
        self.buildPendingTxns(peers[0])
        return peers
    
    def getBlockToMine(self, myPubKey):
        cur = 0
        fee = 0
        blockeReward = 0
        maxSize = 116
        target = self.currentTarget
        index = self.numBlocks + 1
        parentHash = self.chain[-1].parentHash
        txnToMine = []

        while not len(self.pendingTxn) > 0:
            time.sleep(1)

        while cur < len(self.pendingTxn) :
            maxSize += len(self.pendingTxn[cur].txnToByteArray())
            if maxSize > 1000116:
                break
            
            txnValid, reward = self.pendingTxn[cur].verifyTxn()
            if txnValid:
                txnToMine.append(self.pendingTxn[cur])
                blockeReward += reward
            cur+=1
        
        coinBaseOutput = Output(noCoins = blockeReward + fee, pubKey = myPubKey)
        coinBaseTxn = Txn()
        coinBaseTxn.makeCoinBaseTxn(coinBaseOutput)
        blockToMine = Block()
        blockToMine.index = index
        blockToMine.txns = txnToMine
        blockToMine.parentHash = parentHash
        blockToMine.target = target

        return blockToMine
