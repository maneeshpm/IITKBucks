# IITKBucks
Contains the IITKBucks client

## Current Status
- Added function `verifyTxn()` to the `txn` class. It performs three tasks:
- - Makes sure every input `inp` is a part of of dictionary `unusedOP` of the form `{(inp.txnID, inp.opIndex) : output object}` using the `ifInpInUnusedOP()` function.
- - Verifies the signature of every input using `verifySign()` function.
- - Ensures that the number of output coins is not more than the number of input coins.