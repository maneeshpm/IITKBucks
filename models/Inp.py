class Inp:
    def __init__(self, txnID, opIndex, sign):
        self.txnID = txnID
        self.opIndex = opIndex
        self.sign = sign
        self.lenSign = len(self.sign)

    def getInputBytes(self):
        return ((self.txnID)
        +(self.opIndex.to_bytes(4, byteorder = 'big'))
        +(self.lenSign.to_bytes(4, byteorder = 'big'))
        +(self.sign))
    
    def __str__(self):
        pr = ("\t\tTransaction ID: {}\n".format(self.txnID.hex())
        +"\t\tIndex: {}\n".format(self.opIndex)
        +"\t\tLength of signature: {}\n".format(self.lenSign)
        +"\t\tSignature: {}\n".format(self.sign.hex()))
        return pr          
