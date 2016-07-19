package ethereumGen;

import java.util.List;

public class ResponseGetBlock {
	
	int status;
	List<Transaction> data;
	
	public ResponseGetBlock(){
		
	}
	
	public int getStatus() {
		return status;
	}
	public void setStatus(int status) {
		this.status = status;
	}
	@Override
	public String toString() {
		return "ResponseGetBlock [status=" + status + ", data=" + data + "]";
	}
	public List<Transaction> getData() {
		return data;
	}
	public void setData(List<Transaction> data) {
		this.data = data;
	}

	
}

class Transaction{
	public Transaction(){
	}
	
	String hash;
	String sender;
	String recipient;
	String accountNonce;
	long price;
	long gasLimit;
	long amount;
	long block_id;
	String time;
	long newContract;
	String isContractTx;
	String blockHash;
	String parentHash;
	String txIndex;
	long gasUsed;
	@Override
	public String toString() {
		return "Transaction [hash=" + hash + ", sender=" + sender + ", recipient=" + recipient + ", accountNonce="
				+ accountNonce + ", price=" + price + ", gasLimit=" + gasLimit + ", amount=" + amount + ", block_id="
				+ block_id + ", time=" + time + ", newContract=" + newContract + ", isContractTx=" + isContractTx
				+ ", blockHash=" + blockHash + ", parentHash=" + parentHash + ", txIndex=" + txIndex + ", gasUsed="
				+ gasUsed + "]";
	}
}
