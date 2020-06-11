from flask import Flask, jsonify, Request
from models.Block import Block
from models.Blockchain import Blockchain 
app = Flask(__name__)

blockchain = Blockchain()

@app.route('/')
def home():
    return "<h3>\"Rabbit, Fire up the server!\"</h3>Thor,<br>The strongest avenger"

@app.route('/getBlock/<n>')
def getBlock(n):
    pass

@app.route('getPendingTransactions')
def getPendingTransactions():
    return jsonify(blockchain.getPendingTxnJSON())
