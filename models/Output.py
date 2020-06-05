class Output:
    def __init__(self, noCoins, pubKey):
        self.noCoins = noCoins
        self.pubKey = pubKey
        self. lenPubKey = len(self.pubKey)

    def getOutputBytes(self):
        return (self.noCoins.to_bytes(8, byteorder = 'big')
        +self.lenPubKey.to_bytes(4,byteorder = 'big')
        +self.pubKey)

    def __str__(self):
        pr = ("\t\tNumber of coins: {}\n".format(self.noCoins)
        +"\t\tLength of public key: {}\n".format(self.lenPubKey)
        +"\t\tPublic key: {}\n".format(self.pubKey.decode()))
        return pr

