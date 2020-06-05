import hashlib

class Inp:
    def __init__(self, txnID, opIndex, sign):
        self.txnID = txnID
        self.opIndex = opIndex
        self.sign = sign
        self.lenSign = len(self.sign)

    def getBinaryInput(self):
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

class Output:
    def __init__(self, noCoins, pubKey):
        self.noCoins = noCoins
        self.pubKey = pubKey
        self. lenPubKey = len(self.pubKey)

    def getBinaryOutput(self):
        return (self.noCoins.to_bytes(8, byteorder = 'big')
        +self.lenPubKey.to_bytes(4,byteorder = 'big')
        +self.pubKey)

    def __str__(self):
        pr = ("\t\tNumber of coins: {}\n".format(self.noCoins)
        +"\t\tLength of public key: {}\n".format(self.lenPubKey)
        +"\t\tPublic key: {}\n".format(self.pubKey.decode()))
        return pr

class Txn:
    totInput=[]
    totOutput=[]
    def _init_(self):
        self.noInputs = 0
        self.noOutputs = 0
        self.totInput = []
        self.totOutput = []

    def getTxnData(self):
        data = self.noInputs.to_bytes(4, byteorder = 'big')
        for inps in self.totInput:
            data += inps.getBinaryInput()
        data += (self.noOutputs.to_bytes(4, byteorder = 'big'))
        for ops in self.totOutput:
            data += (ops.getBinaryOutput())
        return data

    def getTxnHash(self):
        h = hashlib.sha256()
        h.update(self.getTxnData())
        return h.hexdigest()
    
    def getTxnDetails(self):
        print("Transaction ID: {}\n".format(self.getTxnHash()))
        print("\nNumber of inputs: {}\n".format(self.noInputs))
        for i in range(self.noInputs):
            print("\tInput #{}:\n".format(i+1))
            print(self.totInput[i])
        print("\nNumber of outputs: {}\n".format(self.noOutputs))
        for i in range(self.noOutputs):
            print("\tOutput #{}:\n".format(i+1))
            print(self.totOutput[i])
    
    def generateTxnFile(self):
        with open(str(self.getTxnHash())+".dat",'wb') as f:
            f.write(self.getTxnData())

        print(str(self.getTxnHash())+".dat created successfully!")
    
    def readTxnFile(self, path):
        with open(path, 'rb') as txnFile:
            self.noInputs = int.from_bytes(txnFile.read(4), 'big')
            for _ in range(self.noInputs):
                txnID = txnFile.read(32)
                opIndex = int.from_bytes(txnFile.read(4), 'big')
                signLen = int.from_bytes(txnFile.read(4), 'big')
                sign = bytes.fromhex(txnFile.read(signLen).hex())
                inp = Inp(txnID, opIndex, sign)
                self.totInput.append(inp)

            self.noOutputs = int.from_bytes(txnFile.read(4), 'big')
            for _ in range(self.noOutputs):
                noCoins = int.from_bytes(txnFile.read(8), 'big')
                lenPubKey = int.from_bytes(txnFile.read(4), 'big')
                pubKey = txnFile.read(lenPubKey)
                op = Output(noCoins, pubKey)
                self.totOutput.append(op)