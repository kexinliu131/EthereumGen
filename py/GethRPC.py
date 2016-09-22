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


    # not tested yet
    def call(self, from_addr , to_addr, gas=0 , gas_price=0, value=0, data=""):
        params = {"to":to_addr}

        if not from_addr=="":
            params["from"] = from_addr
        if not gas==0:
            params["gas" == gas]
        if not gas_price == 0:
            params["gas_price"] = gas_price
        if not value == 0:
            params["value"] = value
        if not data == "":
            params["data"] = data
        
        payload = {
            "jsonrpc":"2.0",
            "method":"eth_call",
            "params":[params],
            "id":1
        }
        
        response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()
        return str(response)
        
def main():
    cont = GethRPCController("localhost","8101")
    #print cont.getAccounts()
    #print cont.getBlockNumber()
    print cont.getBalance(cont.getAccounts()[0])
    return

if __name__ == "__main__":
    main()
