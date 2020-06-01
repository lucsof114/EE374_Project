import numpy as np 
from args import load_params
from blocks import *
from scipy.stats import poisson


class Prism: 
    def __init__(self) : 
        ###################### GET PARAMS ############################
        self.params = load_params() #Load paramaters
        self.numVoterChains = self.params["num_voter_chains"]
        self.lp = self.params["lp"]
        self.lv = self.params["lv"]
        self.lt = self.params["lt"]
        self.l = self.lp + self.lv * self.numVoterChains + self.lt
        self.beta = self.params["beta"]
        self.lh = self.l * (1 - self.params["beta"])
        self.la = self.l * self.params["beta"]
        self.txPerBlock = self.params["txPerBlock"]
        self.delta = self.params["prop_delay"] + self.params["communication_cost"] * np.log2(self.numVoterChains + self.txPerBlock)
        self.alpha = self.delta*self.lv
        self.epsilon = self.params["reversal_prob"]


        ###################### INIT SIM VARS #########################
        self.time = 0 #Simulation time
        self.voterChains = [VoterChain(i) for i in range(self.numVoterChains)]
        self.proposerChain = ProposerChain()
        self.txchain = TxChain(self.txPerBlock)
        self.superBlock = SuperBlock(self.numVoterChains)
        self.nextsuperBlock = SuperBlock(self.numVoterChains)
        self.levelMap = {}
        self.propMap = {}
        self.leaderSequence = []
        self.ledger = []
        self.txPerSec = None
        self.confirmation_latency = []
        self.numBlocksMinded = 0

    def stepForward(self) : 
        # update super block
        self.superBlock = self.nextsuperBlock
        self.txchain.curr = len(self.txchain.txList)* self.txPerBlock ## to be removed
        #Mine Block
        self.time += np.random.exponential(1/self.lh) + self.delta
        numForked = np.random.poisson(self.lh*self.delta)
        self.numBlocksMinded += numForked + 1
        #print(self.numBlocksMinded)
        for _ in range(numForked + 1): # number of forked blocks plus one none forked block
            self.getNewBlock()
        if self.numBlocksMinded - self.params["eval_every"] > 0:
            self.numBlocksMinded = 0
            self.updateMaps()
            self.updateProb()
            self.updateLedger()
        

    def updateLedger(self):
        for i, leader in enumerate(self.leaderSequence): 
            blk = self.proposerChain.propList[leader]
            if i > 0 and self.leaderSequence[i - 1] in blk.parent:
                blk.parent.remove(self.leaderSequence[i-1])
            for par in blk.parent:
                parblk = self.proposerChain.propList[par]
                for txind in parblk.txRefs:
                    self.ledger.append(self.txchain.txList[txind].txs)
            for txind in blk.txRefs:
                self.ledger.append(self.txchain.txList[txind].txs)
        self.txPerSec = len(self.ledger)*self.txPerBlock/self.time
        print(self.txPerSec)
    
    def updateMaps(self): 
        self.levelMap = {}
        self.propMap = {}
        for i in range(self.numVoterChains): 
            vchain = self.voterChains[i]
            if not vchain.isgenesis: 
                voternodes = vchain.getlongestpath()
                for vnode in voternodes:
                    for prop in vnode.reference_link:
                        self.proposerChain.propList[prop].numVotes += 1
                        if prop in self.propMap:
                            if not (i, vnode.ind) in self.propMap[prop]: 
                                self.propMap[prop].append((i, vnode.ind))
                        else :
                            self.propMap[prop] = [(i,vnode.ind)]

        for node in self.proposerChain.propList :
            if node.level in self.levelMap: 
                if not node.ind in self.levelMap[node.level]:
                    self.levelMap[node.level].append(node.ind)
            else: 
                self.levelMap[node.level] = [node.ind]

                     

    def updateProb(self):
        ep = self.epsilon 
        self.leaderSequence = []
        for level in self.levelMap: 
            dbar = 0
            sumVotes = 0
            for bp in self.levelMap[level]:
                if bp not in self.propMap:
                     return
                for i, bv in self.propMap[bp]:
                    dbar += self.voterChains[i].voterList[bv].depth
                sumVotes += self.proposerChain.propList[bp].numVotes
                self.proposerChain.propList[bp].numVotes = 0 ## maybe

            dbar /= sumVotes
            da = self.beta*dbar/((1-self.alpha)*(1-self.beta))
            va = self.numVoterChains
            for bp in self.levelMap[level]:
                mu_i = 0
                sigma_i = 0
                for i, bv in self.propMap[bp]:
                    dij = self.voterChains[i].voterList[bv].depth
                    Pij = poisson.cdf(dij, da)
                    for k in range(dij + 1):
                        Pij -= poisson.pmf(k, da)*(self.beta/(1-self.beta))**(dij + 1 - k) 

                    mu_i += Pij 
                    sigma_i += Pij*(1-Pij)
                vi_lower = mu_i - np.sqrt(sigma_i*(np.log(1/ep**2) - np.log(np.log(1/ep**2)) - np.log(2*np.pi)))
                va -= vi_lower
                self.proposerChain.propList[bp].revProbLow = vi_lower
            for bpL in self.levelMap[level]:
                isleader = True
                vl = self.proposerChain.propList[bpL].revProbLow
                for bpi in self.levelMap[level]:                    vih = self.proposerChain.propList[bpi].revProbLow + va
                    if vl < vih or vl < va: 
                        isleader = False
                if isleader: 
                    self.proposerChain.propList[bpL].isLeader = True
                    dt = self.time -  self.proposerChain.propList[bpL].time
                    self.confirmation_latency.append(dt)
                    self.leaderSequence.append(bpL)
                else:
                    isleader = True
                    assert self.proposerChain.propList[bpL].isLeader == False, "persistance failed!"
                    break
            
    def getNewBlock(self): 
        sortition = np.random.uniform(0, self.l)
        thresh = 0
        for i in range(self.numVoterChains): 
            thresh += self.lv
            if sortition < thresh:
                self.voterChains[i].addBlock(self.superBlock)
                self.nextsuperBlock.Cvoter[i] = []
                self.nextsuperBlock.vParent[i] = self.voterChains[i].getTip()
                return 
        thresh += self.lp
        if sortition < thresh: 
            self.proposerChain.addBlock(self.superBlock, self.time)
            self.nextsuperBlock.loneTx = []
            tip = self.proposerChain.getTip()
            self.nextsuperBlock.propParent = tip
            for j in range(self.numVoterChains):
                self.nextsuperBlock.Cvoter[j].append(tip[0])  ### to be changed for forking
            return
        thresh += self.lt
        if sortition < thresh: 
            tip = self.txchain.addBlock()
            self.nextsuperBlock.loneTx.append(tip)

#### DEBUG ###### 
if __name__ == "__main__":
    p = Prism()
    while True:
        p.stepForward()