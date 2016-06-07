__author__ = 'Thomas Rueckstiess, ruecksti@in.tum.de'


from learning import LearningAgent
from policygradient import PolicyGradientAgent
from pybrain.structure import StateDependentLayer, IdentityConnection
from pybrain.tools.shortcuts import buildNetwork


class StateDependentAgent(PolicyGradientAgent):
    """ StateDependentAgent is a learning agent, that adds a GaussianLayer to its module and stores its
        deterministic inputs (mu) in the dataset. It keeps the weights of the exploration network
        constant for a whole episode which creates smooth trajectories rather than independent random 
        perturbations at each timestep. See "State-Dependent Exploration for Policy Gradient Methods",
        ECML PKDD 2008.
    """
    
    def __init__(self, module, learner = None):
        LearningAgent.__init__(self, module, learner)
        
        # exploration module (linear flat network)
        self.explorationmodule = buildNetwork(self.indim, self.outdim, bias=False)
        
        # state dependent exploration layer
        self.explorationlayer = StateDependentLayer(self.outdim, self.explorationmodule, 'explore')
                
        # add exploration layer to top of network through identity connection
        out = self.module.outmodules.pop()
        self.module.addOutputModule(self.explorationlayer)
        self.module.addConnection(IdentityConnection(out, self.module['explore'], self.module))
        self.module.sortModules()
        
        # tell learner the new module
        self.learner.setModule(self.module)
        
        # add the log likelihood (loglh) to the dataset and link it to the others
        self.history.addField('loglh', self.module.paramdim)
        self.history.link.append('loglh')
        self.loglh = None
        
        # if this flag is set to True, random weights are drawn after each reward,
        # effectively acting like the vanilla policy gradient alg.
        self.actaspg = False

    def newEpisode(self):
        LearningAgent.newEpisode(self)
        self.explorationlayer.drawRandomWeights()

    def getAction(self):
        self.explorationlayer.setState(self.lastobs)
        action = PolicyGradientAgent.getAction(self)
        return action
        
    def giveReward(self, r):
        PolicyGradientAgent.giveReward(self, r)
        if self.actaspg:
            self.explorationlayer.drawRandomWeights()