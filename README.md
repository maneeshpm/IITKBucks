# IITKBucks
Contains the IITKBucks client

## Current Status
- Added `/newPeer`, `/getPeers`, `/newBlock`, `/newTransaction` endpoints.
  - `/newPeer` accept json post request of form `{'url':'url of the new peer'}`.
  - `/getPeers` return the peers list as json data `{'peers':[....]}`.
  - `/newBlock` accept post reqeust of binary block data and adds it to the blockchain.
  - `/newTransaction` accepts transaction data in json format as below and adds it to a list of pending transaction after converting into a transaction object.

- Added `/getPendingTransactions` route that accepts a `GET` request and responds with pending transactions in `application/json` content-type.
  - Response JSON format:
  ```
  {
    [
        {
            "inputs": [
                {
                    "transactionID": "<in hex format>",
                    "index": <int>,
                    "signature": "<in hex format>"
                },
                ...
            ],
            "outputs": [
                {
                    "amount": <number of coins int>,
                    "recipient": "<public key of recipient>"
                },
                ...
            ]
        },
        ...
    ]
  }
  ```

- Added function `verifyTxn()` to the `txn` class. It performs three tasks:
  - Makes sure every input `inp` is a part of of dictionary `unusedOP` of the form `{(inp.txnID, inp.opIndex) : output object}` using the `ifInpInUnusedOP()` function.
  - Verifies the signature of every input using `verifySign()` function.
  - Ensures that the number of output coins is not more than the number of input coins.