import numpy as np 
from args import load_params
from blocks import *


class Prism: 
    def __init__(self) : 
        ###################### GET PARAMS ############################
        self.params = load_params() #Load paramaters
        self.numVoterChains = self.params["num_voter_chains"]
        self.lp = self.params["lp"]
        self.lv = self.params["lv"]
        self.lt = self.params["lt"]
        self.l = self.lp + self.lv * self.numVoterChains + self.lt
        self.lh = self.l * (1 - self.params["beta"])
        self.la = self.l * self.params["beta"]
        self.delta = self.params["prop_delay"] + self.params["communication_cost"] * np.log2(self.numVoterChains + self.txPerBlock)
        self.txPerBlock = self.params["txPerBlock"]


        ###################### INIT SIM VARS #########################
        self.time = 0 #Simulation time
        self.voterChains = [VoterChain(i) for i in range(self.numVoterChains)]
        self.proposerChain = ProposerChain()
        self.txchain = TxChain(self.txPerBlock)
        self.superBlock = SuperBlock(self.numVoterChains)
        self.nextsuperBlock = SuperBlock(self.numVoterChains)

    def stepForward(self) : 
        # update super block
        self.superBlock = self.nextsuperBlock
        self.txchain.curr += self.txPerBlock ## to be removed
        #Mine Block
        self.time += np.random.exponential(1/self.lh) + self.delta
        numForked = np.random.poisson(self.lh*self.delta)

        for _ in range(numForked + 1): # number of forked blocks plus one none forked block
            self.getNewBlock()
        self.update()
    
    
    def update(self): 
        for node in self.proposerChain.propList :
            node.numVotes = 0 
        for i in range(self.numVoterChains): 
            vchain = self.voterChains[i]
            if not vchain[i].isgenesis: 
                voternodes = vchain.getlongestpath()
                for vnode in voternodes:
                    for prop in vnode.voterList:
                        self.proposerChain.propList[prop] += 1  

                     


    def getNewBlock(self): 
        sortition = np.random.uniform(0, self.l)
        thresh = 0
        for i in range(self.numVoterChains): 
            thresh += self.lv
            if sortition < thresh:
                self.voterChains[i].addBlock(self.superBlock)
                self.nextsuperBlock.Cvoter[i] = None
                self.nextsuperBlock.vParent[i] = self.voterChains[i].getTip()
                return 
        thresh += self.lp
        if sortition < thresh: 
            self.proposerChain.addBlock(self.superBlock)
            self.nextsuperBlock.loneTx = None
            tip = self.proposerChain.getTip()
            self.nextsuperBlock.propParent = tip
            for i in range(self.numVoterChains):
                self.nextsuperBlock.Cvoter[i].append(tip)
            return
        thresh += self.lt
        if sortition < thresh: 
            tip = self.txchain.addBlock()
            self.nextsuperBlock.loneTx.append(tip)
        

    def genNewProposerBlock(self): 
        newBlock = ProposerBlock()

        if len(self.proposerChain.tips) == 0: #genesis 
            newBlock.transRefs = self.availableTransBlocks
            self.proposerChain.addBlock(newBlock)
            
          

    def genNewVoterBlock(self, ind):
        newblock = VoterBlock()
        newblock.reference_links = self.voterchains[ind].availableProps
        for ref in self.voterchains[ind].availableProps: 
            self.proposerChain.addVote(ref)
