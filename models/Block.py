import hashlib
import time
import struct
from models.Txn import Txn
from models.Inp import Inp
from models.Output import Output
import os

class Block:
    #id, index,timestamp,transactions,parenthash,target,nonce
    def __init__(self, id = None, index = None, timestamp = None, txns = None, parentHash = None, target = None, nonce = None):
        self.id = id
        self.index = index
        self.timestamp = timestamp
        self.txns = []
        self.parentHash = parentHash
        self.target = target
        self.nonce = nonce 
        self.body = None
        self.blockBodyHash = None
        
    def txnListFromByteArray(self, data):
        txns = []
        currOffset=0
        noTxns = int.from_bytes(data[currOffset:currOffset+4], 'big')
        currOffset+=4
        for _ in range(noTxns):
            szTxn = int.from_bytes(data[currOffset:currOffset+4],'big')
            currOffset+=4
            txn = Txn()
            txn.txnFromByteArray(data[currOffset:currOffset+szTxn])
            currOffset+=szTxn
            txns.append(txn)
        return txns
    
    def blockFromByteArray(self, data):
        co = 0
        self.index = int.from_bytes(data[co:co+4],'big')
        co+=4
        self.parentHash = data[co:co+32]
        co+=32
        self.blockBodyHash = data[co:co+32]
        co+=32
        self.target = int.from_bytes(data[co:co+32],'big')
        co+=32
        self.timestamp = int.from_bytes(data[co:co+8],'big')
        co+=8
        self.nonce = int.from_bytes(data[co:co+8],'big')
        co+=8
        self.body = data[co:]
        self.txns = self.txnListFromByteArray(data[co:])
        self.header = data[0:116]

    def getHeader(self):
        if self.body == None:
            self.body = self.txnListToByteArray()
        if self.blockBodyHash == None:
            self.blockBodyHash = self.getBodyHash()

        header = (self.index.to_bytes(4,'big')
        + self.parentHash
        + self.blockBodyHash
        + self.target.to_bytes(32,'big')
        + self.timestamp.to_bytes(8,'big')
        + self.nonce.to_bytes(8,'big'))
        return header
    
    def getHeaderHash(self):
        return hashlib.sha256(self.getHeader()).digest()
    
    def getBodyHash(self):
        return hashlib.sha256(self.body).digest()

    def blockToByteArray(self):
        data = self.getHeader()
        bb = None
        if self.body == None:
            bb = len(self.txns).to_bytes(4, 'big')
            for txn in self.txns:
                bb += len(txn.txnToByteArray()).to_bytes(4,'big')
                bb += txn.txnToByteArray()
            self.body = bb
        data += self.body
        return data

    def txnListToByteArray(self):
        data = b''
        for txn in self.txns:
            data += txn.txnToByteArray()
        self.body = data
        return data
    
    def export(self):
        # print(os.getcwd())
        with open('blockchain/blocks/{}.dat'.format(self.index),'wb') as file:
            file.write(self.blockToByteArray())

    def view(self):
        print(f'contains {len(self.txns)} txns')
        for i,txn in enumerate(self.txns):
            print(f'\ttxn {i}, id = {txn.id.hex()}')
            print(f'\t\tcontains {len(txn.totInput)} inputs')
            for inp in txn.totInput:
                print(f'\t\t\t({inp.txnID.hex()}, {inp.opIndex})')
            print(f'\t\tcontains {len(txn.totOutput)} outputs')
            for i, op in enumerate(txn.totOutput):
                print(f'\t\t\t({i}, {txn.id.hex()})\n\t\t\t({op.noCoins})')
                


    # def mine(self):
        
    #     maxNonce = 2**64
    #     print("Mining block")

    #     for i in range(maxNonce):
    #         self.nonce = i
    #         self.timestamp = time.perf_counter_ns()
    #         if int.from_bytes(self.getHeaderHash(), 'big') <= self.target:
    #             print("Nonce Found!")
    #             return True
    


    """
    def setBodyHash(self):
        h = hashlib.sha256()
        h.update(self.body)
        self.bodyHash = bytes.fromhex(h.hexdigest())

    def getHeader(self):
        data = (self.index.to_bytes(4,'big')
        + self.parentHash
        + self.bodyHash
        + self.target.to_bytes(32,'big')
        + bytearray(struct.pack('f',self.timestamp))
        + self.nonce.to_bytes(8,'big'))

        return data

    def getHeaderHash(self):
        h = hashlib.sha256()
        h.update(self.getHeader())
        return h.hexdigest()

    def setNonce(self):
        maxnonce = 2**64
        print("Finding nonce... ")
        t1 = time.perf_counter()
        for i in range(maxnonce):
            self.nonce = i
            self.timestamp = time.time_ns()
            if int(self.getHeaderHash(),16) <= self.target:
                break
        t2 = time.perf_counter()
        print("Nonce found!\nNonce = {}, Timestamp={:0.6f}, Hash={}".format(self.nonce, self.timestamp, self.getHeaderHash()))
        print("Time elapsed = {}m {}s".format(int((t2-t1)/60), int((t2-t1))%60))
            
    def getByteStream(self):
        return self.header + self.body


    def __init__(self, index=None, parentHash=None, body=None, target=None):
        self.index = index
        self.parentHash = parentHash
        self.bodyHash = None
        self.target = target
        self.timestamp = None
        self.nonce = None
        
        self.body = body
        self.header = None
        if index!=None:
            self.setBodyHash()
            self.setNonce()

    """



        
    
    
        