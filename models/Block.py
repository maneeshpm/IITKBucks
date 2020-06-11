import hashlib
import time
import struct

class Block:
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


    def __init__(self, index, parentHash, body, target):
        self.index = index
        self.parentHash = parentHash
        self.bodyHash = None
        self.target = target
        self.timestamp = None
        self.nonce = None
        
        self.body = body
        self.header = None

        self.setBodyHash()

        self.setNonce()





        
    
    
        