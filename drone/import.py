import networkx as nx
import matplotlib.pyplot as plt
import itertools
from networkx.algorithms.matching import max_weight_matching
import random
import pickle
import osmnx as ox
import time
from IPython.display import clear_output

def save_graph(G, nom_fichier):
    nom_fichier = nom_fichier.replace(" ", "-")
    with open(nom_fichier, 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
    print(f"Graphe du quartier sauvegardé dans : {nom_fichier}")

def fetch_arrondissement(arrondissement):
    quartier = "Montréal, Québec, Canada"
    G = ox.graph_from_place(quartier, network_type="drive")
    G = ox.distance.add_edge_lengths(G)
    return G

def import_G(filename):
    #filename = "plateau_mont_royal.gpickle"
    
    with open(filename, 'rb') as f:
        G = pickle.load(f).to_undirected()
    return G

def snowize(G, p = 0.5):
    for u, v in G.edges():
        for key in G[u][v]:
            if (random.random() <= p):
                G[u][v][key]['snow'] = 1
            else:
                G[u][v][key]['snow'] = 0
    return G

def eulerize(G):
    # G_bis = copie de G en Multigraph
    # G_aug = G euleuriser
    G_bis = nx.MultiGraph(G)
    
    # Trouver les sommets de degre impair
    odd_nodes = [v for v, d in G_bis.degree() if d % 2 == 1]
    
    # Generer tous les appariements possibles (pairs sans repetition)
    pairs = list(itertools.combinations(odd_nodes, 2))
    
    # Calculer la distance la plus courte entre chaque paire
    pair_weights = {}
    for u, v in pairs:
        length = nx.dijkstra_path_length(G_bis, u, v, weight='length')
        pair_weights[(u, v)] = length
    
    # Trouver les chemins de distance minimale pour chaque paire de nœuds
    neg_weights = {pair: -w for pair, w in pair_weights.items()}
    matching_graph = nx.Graph([(u, v, {'weight': neg_weights[(u, v)]}) for (u, v) in neg_weights])
    matching = max_weight_matching(matching_graph, maxcardinality=True)
    
    # Ajouter les aretes necessaires (dans un MultiGraph)
    G_aug = nx.MultiGraph(G)  # copie avec aretes multiples autorisees
    for u, v in matching:
        path = nx.dijkstra_path(G, u, v, weight='length')
        path_edges = list(zip(path[:-1], path[1:]))
        for edge in path_edges:
            weight = G_bis[edge[0]][edge[1]][0]['length']
            G_aug.add_edge(edge[0], edge[1], weight=weight)
        
    return G_aug

def circuit(G_aug):
    return list(nx.eulerian_circuit(G_aug))

def snow_roads(G_aug, G_bis):
    circuit = list(nx.eulerian_circuit(G_aug))
    edges = []
    for i, (u, v) in enumerate(circuit):
        for key in G_bis[u][v]:
            if G_bis[u][v][key]['snow']:
                edges.append((u, v, key))

    return edges

def gpickle(arrondissements):
    for arrondissement in arrondissements:
        G = fetch_arrondissement(arrondissement)
        save_graph(G,arrondissement)

def euler_save(arrondissements):
    for arrondissement in arrondissements:
        start = time.time()    
        G = import_G("../database/maps/" + arrondissement.replace(" ", "-") + ".gpickle")
        G_aug = eulerize(G)
        #circuit(G_aug)
         
        save_graph(G_aug, "../database/eulerized_maps/" + arrondissement + "_aug.gpickle")
        end = time.time()

        print(str(end - start) + " secondes")
        
euler_save(["Montréal"])




