import spade, threading

model = None


class MultiAgentModel:
    def __init__(self):
        self.varTable = dict()
        self.agentList = dict()
        self.lock = threading.Lock()

    def start(self):
        for i in range(1, 6):
            self.agentList['user' + str(i)] = MyAgent("agent" + str(i) + "@127.0.0.1", "secret");
            self.agentList['user' + str(i)].start()


class MyAgent(spade.Agent.Agent):
    def _setup(self):
        print "MyAgent starting . . ."
        self.value = 10
        b = MyBehav(self)
        self.addBehaviour(b, None)


class MyBehav(spade.Behaviour.OneShotBehaviour):
    def __init__(self):
        spade.Behaviour.OneShotBehaviour.__init__(self)

    def getBal(self):
        return 1

    def sendTran(self, str):
        print "send transaction dummy"
        pass

def main():

    global model
    model = MultiAgentModel()
    model.start()
    pass

if __name__ == "__main__":
    main()