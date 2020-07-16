import click
import json
import requests
from Crypto.PublicKey import RSA
from models.Output import Output
from models.Inp import Inp
from models.Txn import Txn
from Crypto.Signature import pss
from Crypto.Hash import SHA256

myUrl = 'http://localhost:8080'

@click.group()
def main():
    """
    A simple CLI for IITKBucks service
    """
    click.echo('Welcome to IITKBucks')

@main.command()
@click.argument('alias')
@click.argument('publickeypath')
def addalias(alias, publickeypath):
    """
    Lets you associate an alias with a public key
    """
    pubKey = RSA.import_key(open(publickeypath, 'rb').read())
    reqData = {}
    reqData['alias'] = alias
    reqData['publicKey'] = pubKey
    try:
        r = requests.post(url = myUrl + '/addAlias', json = json.dumps(reqData))
    except:
        print('[ERROR] connection declined')
        return
    if r.status_code == 200:
        click.echo('[SUCCESS] Alias added!')
    else:
        click.echo('[WARNING] Adding alias failed.')

@main.command()
def generatekeys():
    """
    Lets you generate a public-private RSA key pair so that you can register as a user 
    """
    key = RSA.generate(2048)
    private_key = key.export_key("PEM")
    file_out = open("private.pem", "wb")
    file_out.write(private_key)
    file_out.close()

    public_key = key.publickey().export_key("PEM")
    file_out = open("public.pem", "wb")
    file_out.write(public_key)
    file_out.close()
    click.echo('[SUCCESS] Keys generated! find them in this directory.')

@main.command()
@click.option('--alias', default = None, help = 'provide an alias')
@click.option('--publickey', default = None, help = 'provide the path of the public key')
def balance(alias, publickey):
    """
    Check balance in your wallet
    """
    query = {}
    if publickey is not None:
        query['publicKey'] = RSA.import_key(open(publickey, 'rb').read())
    if alias is not None:
        query['alias'] = alias
    try:
        r = requests.post(url = myUrl+'/getUnusedOutputs', json = json.dumps(query))
    except:
        print('[ERROR] connection declined')
        return
    if r.status_code != 200:
        click.echo('[WARNING ]query failed!')
    else:
        bal = 0
        for ops in r.json()['unusedOutputs']:
            bal += ops['amount']
        click.echo(f'[SUCCESS] you have {bal} coins in the wallet.')

@main.command()
@click.argument('publicKeyPath')
@click.argument('privateKeyPath')
def txn(publicKeyPath, privateKeyPath):
    """
    Generate txns
    """
    publicKey = RSA.import_key(open(publicKeyPath, 'rb').read())
    privateKey = RSA.import_key(open(privateKeyPath, 'rb').read())
    try:
        r = requests.post(url = myUrl+'/getUnusedOutputs', json = json.dumps({'publicKey':publicKey}))
    except:
        print('[ERROR] connection declined.')
        return
    balance = 0
    inputsData = []
    if r.status_code != 200:
        click.echo('[WARNING] query failed!')
        return
    else:
        inputsData = r.json()['unusedOutputs']
        for ops in inputsData:
            balance += ops['amount']
        click.echo(f'you have {balance} coins in the wallet.')
    numberOfOutputs = int(input('Enter the number of outputs to generate: '))
    outputs = []
    opCoins = 0
    for i in range(numberOfOutputs):
        option = input('Do you want to use an alias for recipient or public key? (a/p): ')
        pubKey = None
        if option == 'a':
            alias = input('Enter the alias of the recipient: ')
            r = requests.post(url = myUrl+'/getPublicKey', json = json.dumps({'alias':alias}))
            if r.status_code != 200:
                click.echo('query failed!')
                return
            pubKey = RSA.import_key(r.json()['publicKey'])
        elif option == 'p':
            path = input('Enter the path of recipient public key: ')
            pubKey = RSA.import_key(open(path, 'rb').read())
        else:
            click.echo('invalid option!')
            return
        coins = int(input('Number of coins to send: '))
        opCoins += coins
        outputs.append(Output(coins, pubKey))

    txnFee = int(input('enter the txn fees: '))
    if balance < opCoins + txnFee:
        click.echo('not enough funds!')
        return
    elif balance > opCoins + txnFee:
        outputs.append(Output(balance - opCoins - txnFee, publicKey))

    txn = Txn()
    txn.totOutput = outputs
    opHash = txn.getOutputHash()
    inputs = []
    for inp in inputsData:
        inputs.append(Inp(
            bytes.fromhex(inp['transactionId']), 
            int(inp['index']),
            pss.new(privateKey, salt_len = 32).sign(SHA256.new(bytes.fromhex(inp['transactionId'])+int(inp['index']).to_bytes(4,'big')+opHash))
        ))
    txn.totInput = inputs
    r = requests.post(url = myUrl + '/newTransaction', json = json.dumps(txn.getTxnJSON())) 
    if r.status_code == 200:
        click.echo('txn generated and sent to server')
    else:
        click.echo('server threw and error')           



if __name__ == '__main__':
    main()