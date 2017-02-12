import spade, threading
import time
import numbers
from EtherHis import Transaction, IntRange


class MultiAgentModel:

    this_model = None
    state_lock = threading.Lock()
    count_lock = threading.Lock()

    def __init__(self, handler=None):
        self.agent_list = dict()
        self.running_agent = 0
        self.handler = handler
        MultiAgentModel.this_model = self # singleton pattern

    def start(self):
        for i in range(0, 6):
            self.agent_list[i] = MyAgent("agent" + str(i) + "@127.0.0.1", "secret");
            self.agent_list[i].id = "user" + str(i)
            self.agent_list[i].start()

    def __str__(self):
        return "MultiAgentModel"

    def run_behaviors(self, state, behav_classes):
        if state.behaviors == []:
            return

        MultiAgentModel.state_lock.acquire()
        self.running_agent += len(state.behaviors)

        for behav in state.behaviors:
            # print str(behav[0]) + "   " + str(behav[1]) + "   " + str(len(behav_classes)) + "   " + str(len(behav))
            MultiAgentModel.this_model.agent_list[behav[0]].addBehaviour(behav_classes[behav[1]]())
            # print "finished add behaviour"
        MultiAgentModel.state_lock.acquire()
        MultiAgentModel.state_lock.release()
        return


class MyAgent(spade.Agent.Agent):
    def _setup(self):
        print "MyAgent starting . . ."
        self.value = 10

class MyBehav(spade.Behaviour.OneShotBehaviour):
    def onStart(self):
        # print "on start"
        pass

    def _process(self):
        # print "on process"
        time.sleep(5)
        pass

    def __init__(self):
        spade.Behaviour.OneShotBehaviour.__init__(self)

    def get_bal(self):
        return MultiAgentModel.this_model.handler.agent_get_bal(self.myAgent.id)

    def onEnd(self):
        # print "on end before acquiring lock"
        MultiAgentModel.count_lock.acquire()
        # print "on end"
        MultiAgentModel.this_model.running_agent -= 1
        MultiAgentModel.count_lock.release()

        if MultiAgentModel.this_model.running_agent == 0:
            MultiAgentModel.state_lock.release()

    def send_tran(self, toAccount, value = IntRange("0"), gas = IntRange("300000"), repeat = IntRange("1"), function = "", param = []):
        print "send transaction in behavior"
        if (isinstance(value, numbers.Integral)):
            value = IntRange(str(value))
        if (isinstance(gas, numbers.Integral)):
            gas = IntRange(str(gas))
        if (isinstance(repeat, numbers.Integral)):
            repeat = IntRange(str(repeat))

        tr = Transaction(self.myAgent.id, toAccount, value, gas, repeat, function, param)
        print "created tr object"
        return MultiAgentModel.this_model.handler.agent_send_tran(tr)

    def __str__(self):
        return "Inherited from MyBehav Object\nclass name:" + str(self.__class__) + "\n\n"


def main():
    model = MultiAgentModel()
    model.start()
    pass

if __name__ == "__main__":
    main()