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
    class MyBehav(spade.Behaviour.OneShotBehaviour):

        def __init__(self, agent, detail):
            spade.Behaviour.OneShotBehaviour.__init__(self)
            self.agent = agent
            self.detail = detail

        global model

        def onStart(self):
            model.lock.acquire()
            print "Starting behaviour . . ."
            self.agent.value += 1

        def _process(self):
            print "Hello World from a OneShot " + str(self.agent.value)

        def onEnd(self):
            print "Ending behaviour . . ."
            model.lock.release()

    def _setup(self):
        print "MyAgent starting . . ."
        self.value = 10
        b = self.MyBehav(self)
        self.addBehaviour(b, None)


def main():

    global model
    model = MultiAgentModel()
    model.start()
    pass

if __name__ == "__main__":
    main()
