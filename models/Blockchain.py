from models.Block import Block
from models.Txn import Txn
from models.Output import Output
import json
import hashlib
from Crypto.Signature import pss
from Crypto.Hash import SHA256
import requests
import time

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.unusedOP = {}
        self.unusedOPMap = {}
        self.pendingTxn = {}
        self.currentTarget = 0x00000f0000000000000000000000000000000000000000000000000000000000
        self.numBlocks = 0
        self.aliasMap = {}

    def addBlock(self, block):
        self.processBlock(block)
        self.chain.append(block.getHeaderHash())
        self.numBlocks += 1
        block.export()

    def isTxnPending(self, txnhash):
        if txnhash in self.pendingTxn.keys():
            return True
        return False

    def isTxnValid(self, txn):
        if not self.isTxnPending(txn.getTxnHash()):
            print('txn not pending')
            return False, 0
        opHash = txn.getOutputHash()
        sumInputs = 0
        for inp in txn.totInput:
            if (inp.txnID, inp.opIndex) not in self.unusedOP.keys():
                print('output invalid')
                return False, 0
            
            verifier = pss.new(self.unusedOP[(inp.txnID, inp.opIndex)].pubKey, salt_bytes = 32)
            h = SHA256.new(inp.TxnID + int.to_bytes(inp.opIndex) + opHash)
            if not verifier.verify(h, inp.sign):
                print('sign invalid')
                return False, 0
            sumInputs += self.unusedOP[(inp.txnID, inp.opIndex)].noCoins
        sumOutputs = txn.getOutputCoins()
        return bool (sumOutputs <= sumInputs), int (sumInputs-sumOutputs)

    def getParentBlockHashTime(self, index):
        if index == -1:
            with open('blockchain/blocks/'+str(0)+'.dat','rb') as genesisblock:
                return bytes.fromhex('0'*64), int.from_bytes(genesisblock[100:108], 'big')
        with open('blockchain/blocks/'+str(index)+'.dat','rb') as blockByteArrar:
            data = blockByteArrar.read()
            return hashlib.sha256(data[:116]).digest(), int.from_bytes(data[100:108], 'big')

    def isBlockValid(self, block):
        if block.index == 0:
            return True
        if block.index != self.numBlocks:
            return False
        parHash, parTime = self.getParentBlockHashTime(self.numBlocks-1)
        if parTime > block.timestamp:
            print('fail timestamp')
            return False
        if block.parentHash != parHash:
            print('fail parenthash')
            return False
        if block.target != self.currentTarget:
            print('fail target')
            return False
        if int.from_bytes(block.getHeaderHash(), 'big') > self.currentTarget:
            print('fail target')
            return False
        
        totalReward = 0
        for i in range(len(block.txns)):
            if i==0: 
                continue
            valid, reward = self.isTxnValid(block.txns[i])
            if not valid:
                print(f'txn {i} failed')
                return False
            totalReward += reward
        return totalReward >= block.txns[0].getOutputCoins()

    def makePendingTxnJSON(self, TxnList):
        # TxnList = json.loads(JSONTxnL)
        for txnData in TxnList:
            txn = Txn()
            txn.makeTxnFromJSON(txnData)
            self.addPendingTxn(txn)
    
    def addPendingTxn(self, txn):
        self.pendingTxn[txn.getTxnHash()] = txn
    
    def removeOPFromUnusedOPMap(self, pubKey, txnIDIndexPair):
        try:
            self.unusedOPMap[pubKey].remove(txnIDIndexPair)
        except:
            print("Output does not exist")

    def addOPToUnusedOPMap(self, pubKey, txnIdIndexPair):
        if pubKey not in self.unusedOPMap:
            self.unusedOPMap[pubKey] = []
        self.unusedOPMap[pubKey].append(txnIdIndexPair)
    
    def processBlock(self, block):
        for txn in block.txns:
            if block.index != 0:
                del self.pendingTxn[txn.getTxnHash()] 
            for inp in txn.totInput:
                op = self.unusedOP[(inp.txnID, inp.opIndex)]
                del self.unusedOP[(inp.txnID, inp.opIndex)]
                self.removeOPFromUnusedOPMap(op.pubKey, (inp.txnID, inp.opIndex))
            for i in range(len(txn.totOutput)):
                self.unusedOP[(txn.id, i)] = txn.totOutput[i]
                self.addOPToUnusedOPMap(txn.totOutput[i].pubKey, (txn.id, i))

    def getPendingTxnJSON(self):
        pendingTxnList = []
        for txn in self.pendingTxn:
            pendingTxnList.append(txn.getTxnJSON())

        return pendingTxnList

    def buildProcessBlock(self, block):
        print(f'contains {len(block.txns)} txns.')

        for txn in block.txns:
            print(f'processing txn {txn.id.hex()}.')
            # print(f'contains {len(txn.totInput)} inputs.') 
            # print(f'contains {len(txn.totOutput)} outputs.')
            for inp in txn.totInput:
                # print(f'removing op ({ inp.txnID.hex()}, {inp.opIndex})')
                op = self.unusedOP[(inp.txnID, inp.opIndex)]
                del self.unusedOP[(inp.txnID, inp.opIndex)]
                self.removeOPFromUnusedOPMap(op.pubKey, (inp.txnID, inp.opIndex))
            # print(f'contains {len(txn.totOutput)} outputs')
            for i in range(len(txn.totOutput)):
                # print(f'adding unused op ({txn.id.hex()}, {i})')
                self.unusedOP[(txn.id, i)] = txn.totOutput[i]
                self.addOPToUnusedOPMap(txn.totOutput[i].pubKey, (txn.id, i))
    
    def buildAddBlock(self, block):
        self.buildProcessBlock(block)
        self.chain.append(block.getHeaderHash())
        self.numBlocks += 1
        block.export()

    def buildBlockchain(self, peer):
        peerGetBlockURL = peer + '/getBlock/'
        i = 0
        while True:
            print(f'getting block {i}...')
            r = requests.get(url = peerGetBlockURL + str(i))
            if r.status_code != 200:
                print(f'[WARNING] stopped at {i} block!')
                break
            block = Block()
            print(f'adding block {i}...')
            block.blockFromByteArray(r.content)
            self.buildAddBlock(block)
            print(f'[SUCCESS] block {i} added!')
            i += 1

    def buildPendingTxns(self, peer):
        peerGetPendingTxnURL = peer+ '/getPendingTransactions/'
        r = requests.get(url = peerGetPendingTxnURL)
        self.makePendingTxnJSON(r.json())
        print('[SUCCESS] Building pending txns complete!')

    
    def initializeBlockchain(self, genesis, myNode):
        print('initializing node...')
        potentialPeers = []
        potentialPeers.append(genesis)
        peers = []
        myUrl = {"url":myNode}
        for potentialPeer in potentialPeers:
            if len(peers)>=5:
                break
            print(f'hit {potentialPeer}')
            r = requests.post(url=potentialPeer+"/newPeer", json=myUrl)
            print(r.status_code)
            if r.status_code == 200:
                print('success!')
                peers.append(potentialPeer)
                potentialPeers.remove(potentialPeer)
            else:
                print('failed!')
                r = requests.get(url = potentialPeer+"/getPeers")
                externalPeers = r.json()["peers"]
                for externalPeer in externalPeers:
                    if externalPeer not in potentialPeers:
                        potentialPeers.append(externalPeer)
        peers.append(genesis)
        print(peers)
        self.buildBlockchain(peers[0])
        print('[SUCCESS] Building blocking complete!\nbuilding pending txns....')
        self.buildPendingTxns(peers[0])
        self.peers = peers
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
            
            txnValid, reward = self.isTxnValid(self.pendingTxn[cur])
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
