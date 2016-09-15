import requests
import json

class GethRPCController:
    def __init__(self,ip,port):
        self.url = "http://" + ip + ":" + port
        self.headers = {'content-type': 'application/json'}

    def getAccounts(self):
        payload = {
		"method": "eth_accounts",
		"jsonrpc": "2.0",
		"id": 0,
	}
        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()
        return [str(unic) for unic in response[u'result']]

    def getBlockNumber(self):
        payload = {
		"method": "eth_blockNumber",
		"jsonrpc": "2.0",
		"id": 0,
	}
        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()
        return int(str(response[u'result']),0)
    def getBalance(self, address, block = "latest"):
        #block is string of an integer or "earliest"/"latest"/"pending"
        payload = {
		"method": "eth_getBalance",
                "params": [address, block],
		"jsonrpc": "2.0",
		"id": 0,
	}
        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()
        return int(response[u'result'],0)
        
def main():
    cont = GethRPCController("localhost","8101")
    #print cont.getAccounts()
    #print cont.getBlockNumber()
    print cont.getBalance(cont.getAccounts()[0])
    return

if __name__ == "__main__":
    main()
