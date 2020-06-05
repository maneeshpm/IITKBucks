import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from Inp import Inp
from Output import Output

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
            data += inps.getInputBytes()
        data += (self.noOutputs.to_bytes(4, byteorder = 'big'))
        for ops in self.totOutput:
            data += (ops.getOutputBytes())
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

    def getOutputHash(self):
        data = b''
        for output in self.totOutput:
            data=data+output.getOutputBytes()
        h = hashlib.sha256()
        h.update(data)
        return h.digest()

    def getOutputCoins(self):
        sumOutput = 0
        for output in self.totOutput:
            sumOutput += output.noCoins
        return sumOutput

    def ifInpInUnusedOP(self, inp, unusedOP):
        #assuming ususedOP is a dictionary of form { (txnID, OPindex) : output object}
        if (inp.txnID, inp.opIndex) in unusedOP:
            return True
        return False

    def verifySign(self, inp, ophash, publicKey):
        toSign = inp.txnID + int.to_bytes(inp.opIndex) + ophash
        verifier = PKCS1_PSS.new(publicKey)
        h = SHA256.new(toSign)
        if verifier.verify(h, inp.sign):
            return True
        return False
    
    def verifyTxn(self, unusedOP):
        ophash = self.getOutputHash()

        sumInp = 0
        sumOutput = self.getOutputCoins()

        for inp in self.totInput:
            if not self.ifInpInUnusedOP(inp, unusedOP):
                return False
            output = unusedOP[(inp.TxnID, inp.opIndex)]
            sumInp += output.noCoins
            
            if not self.verifySign(inp, ophash, output.publicKey):
                return False
        
        if sumOutput > sumInp:
            return False
            
        return True 