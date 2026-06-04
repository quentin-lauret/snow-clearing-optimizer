import sys
import networkx as nx
import time
import pickle

if __name__ == "__main__":
  if len(sys.argv) == 1:
      print("Expecting filename as argument!")
  else:
      for i in range(1, len(sys.argv)):
          print("Opening " + sys.argv[i])
          with open(sys.argv[i], 'rb') as f:
                G = pickle.load(f)

          print('Number of nodes', len(G.nodes))
          print('Number of edges', len(G.edges))
          print('Average degree', sum(dict(G.degree).values()) / len(G.nodes))
          print('Strongly connected', nx.is_strongly_connected(G))
          print()
