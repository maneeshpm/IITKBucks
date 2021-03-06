import hashlib
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_PSS
from Crypto.Hash import SHA256
from models.Inp import Inp
from models.Output import Output
import json

class Txn:
    totInput = []
    totOutput = []

    def _init_(self):
        self.id = None
        self.noInputs = 0
        self.noOutputs = 0
        self.totInput = []
        self.totOutput = []

    def txnToByteArray(self):
        data = self.noInputs.to_bytes(4, byteorder = 'big')
        for inps in self.totInput:
            data += inps.getInputBytes()
        data += (self.noOutputs.to_bytes(4, byteorder = 'big'))
        for ops in self.totOutput:
            data += (ops.getOutputBytes())
        return data

    def getTxnHash(self):
        return hashlib.sha256(self.txnToByteArray()).digest()
    
    def txnFromByteArray(self, data):
        currOffset=0
        self.noInputs = int.from_bytes(data[currOffset:currOffset+4], 'big')
        currOffset+=4
        inputs=[]
        for i in range(self.noInputs):
            txnID = data[currOffset:currOffset+32]
            currOffset+=32
            opIndex = int.from_bytes(data[currOffset:currOffset+4], 'big')
            currOffset+=4
            signLen = int.from_bytes(data[currOffset:currOffset+4], 'big')
            currOffset+=4
            sign = data[currOffset:currOffset+signLen]
            currOffset+=signLen
            inp = Inp(txnID, opIndex, sign)
            inputs.append(inp)
        self.totInput=inputs
        outputs = []
        self.noOutputs = int.from_bytes(data[currOffset:currOffset+4], 'big')
        currOffset+=4
        for i in range(self.noOutputs):
            noCoins = int.from_bytes(data[currOffset:currOffset+8], 'big')
            currOffset+=8
            lenPubKey = int.from_bytes(data[currOffset:currOffset+4], 'big')
            currOffset+=4
            pubKey = data[currOffset:currOffset+lenPubKey]
            currOffset+=lenPubKey
            op = Output(noCoins, pubKey)
            outputs.append(op)
        self.totOutput = outputs
        self.id = self.getTxnHash()

    def getOutputHash(self):
        data = b''
        for output in self.totOutput:
            data += output.getOutputBytes()
        return hashlib.sha256(data).digest()
        
    def getOutputCoins(self):
        sumOutput = 0
        for output in self.totOutput:
            sumOutput += output.noCoins
        return sumOutput

    def makeTxnFromJSON(self, data):
        for inputs in data["inputs"]:
            inp = Inp(bytes.fromhex(inputs["transactionID"]),int(inputs["index"]),bytes.fromhex(inputs["signature"])) 
            self.totInput.append(inp)
            self.noInputs += 1
        
        for outputs in data["outputs"]:
            output = Output(int(outputs["amount"]),outputs["recipient"].encode('utf-8')) 
            self.totOutput.append(output)
            self.noOutputs += 1
    
    def getTxnJSON(self):
        data = {}
        valInputs = []
        for inp in self.totInput:
            curInp = {}
            curInp["transactionID"] = inp.txnID.hex()
            curInp["index"] = inp.opIndex
            curInp["signature"] = inp.sign.hex()
            valInputs.append(curInp)
        
        valOutputs = []
        for op in self.totOutput:
            curOP = {}
            curOP["amount"] = op.noCoins
            curOP["recipient"] = op.pubKey.decode()
            valOutputs.append(curOP)

        data["inputs"] = valInputs
        data["outputs"] = valOutputs

        return data

    def makeCoinBaseTxn(self, output):
        self.noInputs = 0
        self.noOutputs = 1
        self.totInput = []
        self.totOutput.append(output)

    # View Details
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
     