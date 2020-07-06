from flask import Flask, jsonify, Response, request
from models.Block import Block
from models.Blockchain import Blockchain 
from models.Txn import Txn
import requests
from queue import Queue
from threading import Thread, Event
import time
import json

app = Flask(__name__)

blockchain = Blockchain()
peers = []
peerLimit = 5
myNode = '127.0.0.1:8080'
genesisURL = ''

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
    if len(peers)>=peerLimit:
        return "Peer limit exceeded", 500
    if url in peers:
        return "Peer already added", 500    
    peers.append(url)
    return "URL {} added to peers.".format(url)

@app.route('/getPeers')
def getPeers():
    return jsonify({'peers':peers})

@app.route('/newBlock', methods = ['POST'])
def newBlock():
    block = Block()
    block.blockFromByteArray(request.get_data())
    if not blockchain.isBlockValid(block):
        return "Invalid Block", 404
    blockchain.processBlock(block)
    blockchain.addBlock(block)
    
    return "Block added!", 200   

@app.route('/newTransaction', methods = ['POST'])
def newTransaction():
    newTxn = Txn()
    newTxn.makeTxnFromJSON(json.loads(request.get_json()))
    blockchain.addPendingTxn(newTxn)



if __name__ == '__main__':
    app.run(debug = True, port = 8787)
    peers = blockchain.initializeBlockchain(genesisURL, myNode)    
