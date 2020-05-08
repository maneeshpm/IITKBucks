from uuid import uuid4
import json
class output:
    id = None
    amount = 0
    recipient = None

    def __init__(self, amount, recipient):
        self.id = str(uuid4())
        self.amount = amount
        self.recipient = recipient
    
    def serialize(self):
        return str(json.dumps(self.__dict__))

class txn:
    id = None
    inp = None
    outputs = []

    def __init__(self, inp):
        self.id = str(uuid4())
        self.inp = inp

    

    


