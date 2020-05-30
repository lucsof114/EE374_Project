# import networkx as nx
# g = nx.DiGraph()
# g.add_edge(1,2)
# g.add_edge(1,3)
# lp = nx.dag_longest_path(g)
# print(lp)
# g2 = g.copy()
# g2.remove_node(lp[-1])
# lp2 = nx.dag_longest_path(g2)
# print(lp2)
# print(nx.dag_longest_path(g))

from blockchain import Prism
p = Prism()
while True:
    p.stepForward()