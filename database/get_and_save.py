import osmnx as ox
import networkx as nx
import time
import pickle
import sys

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Expecting neighborhood name as argument")
    else:
        # 1. Définir le nom du quartier à extraire
        name = sys.argv[1] 
        quartier = name + ", Montréal, Québec, Canada"

        # 2. Télécharger le graphe routier du quartier
        G = ox.graph_from_place(quartier, network_type="drive")

        # 3. Ajouter la distance (longueur) aux arêtes, si pas déjà incluse
        G = ox.distance.add_edge_lengths(G)

        # 4. Sauvegarder le graphe au format .gpickle
        nom_fichier = "maps/" + name + ".gpickle"
        with open(nom_fichier, 'wb') as f:
            pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
        print(f"Graphe du quartier sauvegardé dans : {nom_fichier}")

'''
ville = "Montréal, Québec, Canada"
'''
