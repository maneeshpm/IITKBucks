from flask import Flask, jsonify, Request, make_response
from models.Block import Block
from models.Blockchain import Blockchain 
app = Flask(__name__)

blockchain = Blockchain()

@app.route('/')
def home():
    return "<h3>\"Rabbit, Fire up the server!\"</h3>Thor,<br>The strongest avenger"

@app.route('/getBlock/<n>')
def getBlock(n):
    data = make_response(blockchain.chain[n].getByteArray())
    data.mimetype = 'application/octet-stream'
    return data

@app.route('getPendingTransactions')
def getPendingTransactions():
    return jsonify(blockchain.getPendingTxnJSON())
