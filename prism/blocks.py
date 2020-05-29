import networkx as nx
class SuperBlock: 
    def __init__(self, numVoter): 
        self.propParent = None
        self.vParent = [None * numVoter]
        self.loneTx = []
        self.Cvoter = [[]*numVoter]


class txBlock: 
    def __init__(self, ref, ind):
        self.txList = ref
        self.ind = ind

class TxChain:
    def __init__(self, TxPerBlock) : 
        self.txPerBlock = TxPerBlock
        self.txchain = []
        self.txlen = 0
        
        ## to be removed 
        self.curr = 0
        ## 

    def addBlock(self): 
        ## to be removed 
        newtx = [i for i in range(self.curr, self.txPerBlock)]
        ##

        newblock = txBlock(newtx, self.txlen)
        self.txchain.append(newblock)
        self.txlen += 1
        return self.txlen




class ProposerBlock: 
    def __init__(self, ref, parent, ind) : 
        self.ind = ind
        self.parent = parent
        self.txRefs = ref
        self.numVotes = 0
        self.revProb = None #Unknown before first sync
        self.isLeader = False


class ProposerChain: 
    def __init__(self): 
        self.chain = nx.DiGraph()
        self.propList = []
        self.propLen = 0
        self.isgenesis = True

    def getTip(self):
        if self.isgenesis: 
            return None
        path = nx.dag_longest_path(self.chain)
        return path[-1]

    def addBlock(self, superblk): 
        parent = superblk.propParent
        newblock = ProposerBlock(superblk.loneTx, parent, self.propLen)
        self.propList.append(newblock)
        self.propLen += 1
        self.chain.add_node(newblock.ind)
        if self.isgenesis: 
            self.isgenesis = False
        else: 
            self.chain.add_edge(parent, newblock.ind)






class VoterBlock:
    def __init__(self, refs, parent, ind ):
        self.reference_link = refs
        self.parent = parent
        self.ind = ind


class VoterChain: 
    def __init__(self, chainID) :
        self.chain = nx.DiGraph() #Genesis block
        self.voterList = []
        self.chainLen = 0
        self.isgenesis = True
        self.chainID = chainID
        self.availableProps = []

    def getTip(self):
        if self.isgenesis: 
            return None
        path = nx.dag_longest_path(self.chain)
        return path[-1]
    
    def getlongestpath(self) : 
        return [self.voterList[idx] for idx in nx.dag_longest_path(self.chain)] 


    def addBlock(self, superblk) : 
        parent = superblk.vParent[self.chainID]
        newBlock = VoterBlock(superblk.Cvoter[self.chainID], parent, self.chainLen)
        self.voterList.append(newBlock)
        self.chainLen += 1
        self.chain.add_node(newBlock.ind)
        if self.isgenesis: 
            self.isgenesis = False
        else: 
            self.chain.add_edge(parent, newBlock.ind)


