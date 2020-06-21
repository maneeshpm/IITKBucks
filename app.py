from flask import Flask
from models.Block import Block
from models.Blockchain import Blockchain 
from models.Txn import Txn
import requests

app = Flask(__name__)
import routes

blockchain = Blockchain()
peers = []
peerLimit = 4
potentialPeers = []
myNode = "127.0.0.1:8080"

def populatePeerList():
    myUrl = {"url":myNode}
    for potentialPeer in potentialPeers:
        if len(peers)>=peerLimit:
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

def removePendingTxn(removeTxnList):
    for txn in blockchain.pendingTxn:
        if txn.id in removeTxnList:
            blockchain.pendingTxn.remove(txn) 

def removeUnusedOP(removeUnusedOPList):
    for OP in removeUnusedOPList:
        blockchain.unusedOP.pop(OP)  

def addUnusedOP(addUnusedOPList):
    for OP in addUnusedOPList:
        blockchain.unusedOP.update({(OP[0],OP[1]) : OP[2]})

def processBlock(block):
    removeTxnList = []
    removeUnusedOPList = []
    addUnusedOPList = []

    for txn in block.txns:
        for inp in txn.totInput:
            removeUnusedOPList.append(inp.txnID, inp.opIndex)
        i=0
        for op in txn.totOutput:
            addUnusedOPList.append(txn.id,i,op)
            i+=1
        removeTxnList.append(txn.id)
    if block.index != 0:    
        removeUnusedOP(removeUnusedOPList)
        removePendingTxn(removeTxnList)
   
    addUnusedOP(addUnusedOPList)



def buildBlockchain():
    peer = peers[0] + "/getBlock/"
    i = 0
    while True:
        r = requests.get(url = peer + i)
        if r.status_code == 404:
            break
        blockData = r.content
        block = Block()
        block.blockFromByteArray(blockData)
        processBlock(block)
        block.export()
        i+=1

def buildPendingTxns():
    r = requests.get(url = peers[0]+"/getPendingTransactions")
    JSONTxnList = r.json()
    blockchain.makePendingTxnJSON(JSONTxnList)

def initialize():
    populatePeerList()
    buildBlockchain()
    buildPendingTxns()

if __name__ == '__main__':
    app.run(debug = True, port = 8787)
    initialize()