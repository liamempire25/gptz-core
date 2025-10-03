import os, json
from web3 import Web3

class TradingAgent:
    def __init__(self, db, bw):
        self.db = db
        self.bw = bw
        self.rpc = os.getenv("ETH_RPC_URL")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc))

    def build_tx(self, to, data, value=0, gas=200000):
        # build unsigned tx and return object for signing
        tx = {"to": to, "value": value, "data": data, "gas": gas}
        return tx

    def propose_tx_to_gnosis(self, tx):
        # Preferred: use Gnosis Safe API to create a tx proposal
        # Do NOT sign with local private keys.
        raise NotImplementedError("Wire up Gnosis Safe relayer here")
