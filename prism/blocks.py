import networkx as nx



class SuperBlock: 
    def __init__(self, numVoter): 
        self.propParent = []
        self.vParent = [None for _ in range(numVoter)]
        self.loneTx = []
        self.Cvoter = [[] for _ in range(numVoter)]


class txBlock: 
    def __init__(self, ref, ind):
        self.txs = ref
        self.ind = ind

class TxChain:
    def __init__(self, TxPerBlock) : 
        self.txPerBlock = TxPerBlock
        self.txList = []
        self.txlen = 0
        
        ## to be removed 
        self.curr = 0
        ## 

    def addBlock(self): 
        ## to be removed 
        newtx = [i for i in range(self.curr, self.curr + self.txPerBlock)]
        ##

        newblock = txBlock(newtx, self.txlen)
        self.txList.append(newblock)
        self.txlen += 1
        return self.txlen - 1




class ProposerBlock: 
    def __init__(self, ref, parent, ind, time) : 
        self.ind = ind
        self.parent = parent
        self.txRefs = ref
        self.level = 0
        self.numVotes = 0
        self.revProbLow =  0 #Unknown before first sync
        self.isLeader = False
        self.time = time #time block was pushed to chain


class ProposerChain: 
    def __init__(self): 
        self.chain = nx.DiGraph()
        self.propList = []
        self.propLen = 0
        self.isgenesis = True
        self.maxlevel = 0

    def getTip(self):
        if self.isgenesis: 
            return None
        
        g = self.chain.copy()
        path = nx.dag_longest_path(g)
        prev = len(path)
        out = []
        while len(path) == prev:
            out.append(path[-1])
            g.remove_node(path[-1])
            path = nx.dag_longest_path(g)
        return out

    def addBlock(self, superblk, time): 
        parent = superblk.propParent
        newblock = ProposerBlock(superblk.loneTx, parent, self.propLen, time)
        self.propLen += 1
        self.chain.add_node(newblock.ind)
        if len(parent) == 0: 
            self.isgenesis = False ## get rid of genesis
        else:
            newblock.level = self.propList[parent[0]].level + 1 
            self.chain.add_edge(parent[0], newblock.ind)
        if newblock.level > self.maxlevel:
            self.maxlevel = newblock.level
        self.propList.append(newblock)






class VoterBlock:
    def __init__(self, refs, parent, ind ):
        self.reference_link = refs
        self.parent = parent
        self.ind = ind
        self.depth = 0


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
        # g = self.chain.copy()
        path = nx.dag_longest_path(self.chain)
        return path[-1]
        # prev = len(path)
        # out = []
        # while len(path) == prev:
        #     out.append(path[-1])
        #     g.remove_node(path[-1])
        #     path = nx.dag_longest_path(g)
        # return out
    

    def getlongestpath(self) : 
        pth = nx.dag_longest_path(self.chain)
        total = len(pth)
        out = []
        for i, p in enumerate(pth):
            self.voterList[p].depth = total - i
            out.append(self.voterList[p])

        return out


    def addBlock(self, superblk) : 
        parent = superblk.vParent[self.chainID]
        newBlock = VoterBlock(superblk.Cvoter[self.chainID], parent, self.chainLen)
        self.chainLen += 1
        self.chain.add_node(newBlock.ind)
        if parent == None: 
            self.isgenesis = False
        else:
            self.chain.add_edge(parent, newBlock.ind)
        self.voterList.append(newBlock)




