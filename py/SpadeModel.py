import spade, threading
import time

model = None

class MultiAgentModel:

    this_model = None
    state_lock = threading.Lock()
    count_lock = threading.Lock()

    def __init__(self, generator=None):
        # self.varTable = dict()
        self.agent_list = dict()
        self.running_agent = 0
        self.generator = generator
        MultiAgentModel.this_model = self # singleton pattern

    def start(self):
        for i in range(0, 6):
            self.agent_list[i] = MyAgent("agent" + str(i) + "@127.0.0.1", "secret");
            self.agent_list[i].start()

    def __str__(self):
        return "MultiAgentModel"

    def run_behaviors(self, state, behav_classes):
        if state.behaviors == []:
            return

        MultiAgentModel.state_lock.acquire()
        self.running_agent += len(state.behaviors)

        for behav in state.behaviors:
            print str(behav[0]) + "   " + str(behav[1]) + "   " + str(len(behav_classes)) + "   " + str(len(behav))
            MultiAgentModel.this_model.agent_list[behav[0]].addBehaviour(behav_classes[behav[1]]())
            print "finished add behaviour"
        MultiAgentModel.state_lock.acquire()
        MultiAgentModel.state_lock.release()
        return


class MyAgent(spade.Agent.Agent):
    def _setup(self):
        print "MyAgent starting . . ."
        self.value = 10

class MyBehav(spade.Behaviour.OneShotBehaviour):
    def onStart(self):
        print "on start"
        pass

    def _process(self):
        print "on process"
        time.sleep(5)
        pass

    def __init__(self):
        spade.Behaviour.OneShotBehaviour.__init__(self)

    def get_bal(self):
        return 1

    def onEnd(self):
        print "on end before acquiring lock"
        MultiAgentModel.count_lock.acquire()
        print "on end"
        MultiAgentModel.this_model.running_agent -= 1
        MultiAgentModel.count_lock.release()

        if MultiAgentModel.this_model.running_agent == 0:
            MultiAgentModel.state_lock.release()

    def send_tran(self, str):
        print "send transaction dummy: " + str
        pass

    def __str__(self):
        return "Inherited from MyBehav Object\nclass name:" + str(self.__class__) + "\n\n"


def main():
    global model
    model = MultiAgentModel()
    model.start()
    pass

if __name__ == "__main__":
    main()