import hashlib
import time
import struct
from models.Txn import Txn
from models.Inp import Inp
from models.Output import Output


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
        
    def txnListFromByteArray(self, data):
        txns = []
        currOffset=0
        noTxns = int.from_bytes(data[currOffset:currOffset+4])
        currOffset+=4
        for _ in range(noTxns):
            szTxn = int.from_bytes(data[currOffset:currOffset+4])
            currOffset+=4
            txn = Txn()
            txn.txnFromByteArray(data[currOffset:currOffset+szTxn])
            currOffset+=szTxn
            txns.append(txn)
        return txns
    
    def blockFromByteArray(self, data):
        self.index = int.from_bytes(data[:4])
        self.parentHash = data[4:36]
        self.blockHash = data[36:68]
        self.target = data[68:100]
        self.timestamp = int.from_bytes(data[100:108])
        self.nonce = int.from_bytes(data[108:116])
        self.body = data[116:]
        self.txns = self.txnListFromByteArray(data[116:])

    def blockToByteArray(self):
        data = (self.index.to_bytes(4,'big')
        + self.parentHash
        + self.blockHash
        + self.target.to_bytes(32,'big')
        + self.timestamp.to_bytes(8,'big')
        + self.nonce.to_bytes(8,'big')
        + self.body)

        return data
    
    def export(self):
        with open('Blocks/{}.dat'.format(self.index),'wb') as file:
            file.write(self.blockToByteArray())

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



        
    
    
        