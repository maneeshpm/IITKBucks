import datetime
import hashlib
import json

class block:
    index = 0
    timestamp = datetime.datetime.now()
    data = None
    parentHash = 0x0
    nonce = 0

    def __init__(self, index, data, prevHash):
        self.index = index
        self.data = data
        self.parentHash = prevHash
        self.nonce = 0
    
    def hashf(self):
        h = hashlib.sha256()
        s = json.dumps(self, default=lambda x: x.__dict__)
        h.update(s.encode('utf-8'))
        return h.hexdigest()
    


