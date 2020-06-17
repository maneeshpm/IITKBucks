from flask import Flask, jsonify, Response, request
from models.Block import Block
from models.Blockchain import Blockchain 
from models.Txn import Txn
app = Flask(__name__)

blockchain = Blockchain()
peers = []
@app.route('/')
def home():
    return "<h3>\"Rabbit, Fire up the server!\"</h3>Thor,<br>The strongest avenger"

@app.route('/getBlock/<n>')
def getBlock(n):
    with open('blockchain/blocks/{}.dat'.format(n),'rb') as blockn:
        data = blockn.read()
        response = Response(response=data, mimetype='application/octet-stream')
        response.headers['Content-Type']='application/octet-stream'
        return response
    
@app.route('/getPendingTransactions')
def getPendingTransactions():
    return jsonify(blockchain.getPendingTxnJSON())

@app.route('/newPeer', methods = ['POST'])
def newPeer():
    url = request.json['url']
    peers.append(url)
    return "URL {} added to peers.".format(url)

@app.route('/getPeers')
def getPeers():
    return jsonify({'peers':peers})

@app.route('/newBlock', methods = ['POST'])
def newBlock():
    blockData = request.get_data()
    block = Block()
    block.blockFromByteArray(blockData)
    blockchain.addBlock(blockData)
    return "Block added!"    

@app.route('/newTransaction', methods = ['POST'])
def newTransaction():
    newTxn = Txn()
    txnJSON = request.get_json()
    newTxn.makeTxnFromJSON(txnJSON)
    blockchain.pendingTxn.append(newTxn)