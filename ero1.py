import networkx as nx
import itertools
from networkx.algorithms.matching import max_weight_matching
import random
import pickle

import os
import copy
import math

quartiers = [
    "anjou",
    "outremont",
    "plateau_mont_royal",
    "riviere-des-prairies-pointe-aux-trembles",
    "verdun"
    ]

def import_G(filename):    
    with open(filename, 'rb') as f:
        G = pickle.load(f)
    return G

def snowize(G, p = 0.5):
    """
    Ajoute de la neige de manière aléatoie sur le graphe

    Pramètres :
        - G : le graphe à enneiger (Graphe)
        - p : La probabilité d'enneiger une arête, avec p = 0.5 par défaut (float)
    
    Retour : le graphe enneigé
    """
    for u, v in G.edges():
        for key in G[u][v]:
            if (random.random() <= p):
                G[u][v][key]['snow'] = 1
            else:
                G[u][v][key]['snow'] = 0
    return G

def snow_roads(G_aug, G_bis):
    """
    Retourne la liste des sommets enneigés

    Pramètres :
        - G_aug : Version eulerianizée du graphe (Graphe)
        - G_bis : Le multigraphe enneigé (Graphe)
    
    Retour : Une liste d'arêtes enneigées de la forme [(u, v, key), ...]
    """
    circuit = list(nx.eulerian_circuit(G_aug))
    edges = []
    for i, (u, v) in enumerate(circuit):
        for key in G_bis[u][v]:
            if G_bis[u][v][key]['snow']:
                edges.append((u, v, key))

    return edges

def fix_edges(G, edges):
    for i in range(len(edges)):
        if not edges[i][1] in G[edges[i][0]]:
            edges[i] = (edges[i][1], edges[i][0], edges[i][2])

def load_floyd_warshall(quartier):
    predecessores, weights = None, None

    # name of the archive where the result of floyd warshall are saved
    FW_file = "database/floyd_warshall_data/" + quartier + "-FWR.pkl"

    if not os.path.exists(FW_file):

        predecessors, weights = nx.floyd_warshall_predecessor_and_distance(G, weight="length")

        predecessors_clean = {u: dict(v) for u, v in predecessors.items()}
        weights_clean = {u: dict(v) for u, v in weights.items()}

        with open(FW_file, "wb") as f:
            pickle.dump((predecessors_clean, weights_clean), f)
    else:
        with open(FW_file, "rb") as f:
            predecessors, weights = pickle.load(f)
    return weights, predecessors
def get_min_in_dict(d):
    curr_min = None
    min_res = None
    for key, item in d.items():
        if curr_min == None or curr_min > item["length"]:
            curr_min = item["length"]
            min_res = key
    return min_res

# converts a list of nodes to a list of (A, B, z)
def add_path_route(graph, path):
    res = []
    for i in range(len(path) - 1):
        a,b = path[i], path[i+1]
        c = get_min_in_dict(graph[a][b])
        
        res.append((a, b, c))
    return res

def is_accessible(dist_floyd, edge, curr_pos):
    return not (dist_floyd[0][curr_pos][edge[0]] == float("inf") and dist_floyd[0][curr_pos][edge[0]] == float("inf"))

def count_accessible(dist_floyd, edges, curr_pos):
    return sum(map(lambda edge: is_accessible(dist_floyd, edge, curr_pos), edges))

def get_shortest_path(graph, dist_floyd, curr_pos, edge):
    target_node = -1
    # on check par ou on peut traverser l'edge

    # gets the weight of each path in order to compare them
    path1_weight = dist_floyd[0][curr_pos][edge[0]]
    path2_weight = dist_floyd[0][curr_pos][edge[1]]
    if path1_weight == float("inf") and path2_weight == float("inf"):
        # print("INACCESSIBLE EDGE")
        return None

    # checks for inability to travel from one node to the other
    if not (edge[1] in graph[edge[0]]):
        nodes = nx.reconstruct_path(curr_pos, edge[0], dist_floyd[1])
        if path2_weight == float("inf"):
            # print("INACCESSIBLE EDGE")
            return None
        return (path2_weight, add_path_route(graph, nodes) + [(edge[1], edge[0], edge[2])])
    if not (edge[0] in graph[edge[1]]):
        # print(f"[DEBUG] edge: {edge}, curr_pos: {curr_pos}, pathlen1: {path1_weight}, pathlen2: {path2_weight}")
        if path1_weight == float("inf"):
            # print("INACCESSIBLE EDGE")
            return None
        nodes = nx.reconstruct_path(curr_pos, edge[1], dist_floyd[1])
        return (path1_weight, add_path_route(graph, nodes) + [(edge[0], edge[1], edge[2])])
    if path1_weight < path2_weight:
        nodes = nx.reconstruct_path(curr_pos, edge[1], dist_floyd[1])
        return (path1_weight, add_path_route(graph, nodes) + [(edge[0], edge[1], edge[2])])
    nodes = nx.reconstruct_path(curr_pos, edge[0], dist_floyd[1])
    return (path2_weight, add_path_route(graph, nodes) + [(edge[1], edge[0], edge[2])])

def getPaths(graph, dist_floyd, targets, starting_pos):
    # on considere uniquement une seule snow plow pour le moment
    start = starting_pos
    unaccessible_count = len(targets) - count_accessible(dist_floyd, targets, starting_pos)
    
    curr_pos = start
    sp_traversal = []
    while len(targets) > 0:
        nearest_snow = (0, get_shortest_path(graph, dist_floyd, curr_pos, targets[0]))

        cpt = 0
        for i in range(1, len(targets)):
            tmp = get_shortest_path(graph, dist_floyd, curr_pos, targets[i])
            if not tmp:
                continue

            if not nearest_snow[1] or tmp[0] < nearest_snow[1][0]:
                #print(count_accessible(dist_floyd, targets, tmp[1][-1][1]))
                if count_accessible(dist_floyd, targets, tmp[1][-1][1]) >= (len(targets) - unaccessible_count) / 2:
                    nearest_snow = (i, tmp)
                else:
                    cpt += 1
        #print(f"cpt: {cpt}")

        if not nearest_snow[1]:
            return sp_traversal
        curr_pos = nearest_snow[1][1][-1][1]

        #print(f"New pos has access to {count_accessible(dist_floyd, targets, curr_pos)} out of {len(targets) - unaccessible_count} accessible targets.")

        sp_traversal += nearest_snow[1][1]
        targets.pop(nearest_snow[0])

    return sp_traversal

def circuit(G_aug):
    return list(nx.eulerian_circuit(G_aug))

def edge_dist(G, edge):
    (x,y,n) = edge
    return G[x][y][n]['length']

def get_total_dist(G, edges):
    res  = 0
    for edge in edges:
        #print(edge)
        try:
            res += edge_dist(G, edge)
        except:
            res = res
    return res
    #return sum(map(lambda edge: edge_dist(G, edge), edges))

def sum_dist(G):
    s = 0
    for u, v in G.edges():
        for key in G[u][v]:
            s += G[u][v][key]['length']
    return s

def sum_dist_circuit(G_bis, circuit):
    s = 0
    for i, (u, v) in enumerate(circuit):
        for key in G_bis[u][v]:
            if G_bis[u][v][key]['length']:
                s += G_bis[u][v][key]['length']
    return s


def charue_stat(nb_km, vitesse, cout, cout_fixe):
    temps_I = nb_km / vitesse
    nb_h = math.floor(temps_I)
    nb_minutes = round((temps_I - nb_h) * 60)
    #print(" - Un temps de", nb_h, "heures et", round((temps_I - nb_h) * 60), "minutes.")
    #print(" - Un cout fixe de", round(cout_fixe,2), "€.")
    cout_kilometrique = cout * nb_km
    #print(" - Un cout kilometrique de", round(cout_kilometrique, 2), "€.")
    if temps_I <= 8:
        cout_horaire = temps_I * cout
    else:
        cout_horaire = 8 * cout + (temps_I - 8) * (cout + 0.2)

    #print(" - Un cout horaire de", round(cout_horaire, 2), "€.")
    cout_total = cout_fixe + cout_kilometrique + cout_horaire
    #print(" - Un cout total de", cout_total, "€.")
    return round(cout_total, 2), temps_I

def is_accessible2(G, floyd_weight, node, max_cpt):
    cpt = 0
    for n in G.nodes():
        if floyd_weight[n][node] != float('inf'):
            cpt += 1
            if cpt >= max_cpt:
                return True
    return False

def find_center(G, floyd_weight):
    sx = 0
    sy = 0
    cpt = 0
    for _, data in G.nodes(data=True):
        if "x" in data and "y" in data:
            cpt += 1
            sx += data["x"]
            sy += data["y"]
    return (sx / cpt, sy / cpt)

def nearest_node(G, coords):
    curr_edge = None
    curr_dist = float("inf")
    for n1, n2, edge_data in G.edges(data=True):
        if "geometry" in edge_data:
            x, y = average_pos(edge_data)
            dist = abs(coords[0] - x) + abs(coords[1] - y)
            if dist < curr_dist:
                curr_dist = dist
                curr_edge = (n1, n2)

    return curr_edge[0]

def find_node_by_pos(G, floyd_weight, coords):
    curr_node = None
    curr_dist = float("inf")
    for n, data in G.nodes(data=True):
        if "x" in data and "y" in data:
            x, y = data["x"], data["y"]
            dist = abs(coords[0] - x) + abs(coords[1] - y)
            if dist < curr_dist and is_accessible2(G, floyd_weight, n, 10):
                curr_dist = dist
                curr_node = n

    return curr_node

def get_starting_point(G, dist_floyd):
    res = None
    res_total_length = float("inf")
    for node in G.nodes:
        res = node
        break;
    for node in G.nodes:
        curr_total = -1
        for dist in dist_floyd[0][node]:
            if dist != float("inf"): #On somme les dist pour aller à tous les points sauf ceux inaccessibles
                curr_total += dist
        if curr_total != -1 and curr_total < res_total_length:
            res = node
            res_total_length = curr_total
    return res

def get_extremums(G, floyd_weight):
    xmax = float("inf")
    xmin = -float("inf")
    ymax = float("inf")
    ymin = -float("inf")
    for _, data in G.nodes(data=True):
        if "x" in data and "y" in data:
            x, y = data["x"], data["y"]
            
            if xmax > x:
                xmax = x
            if xmin < x:
                xmin = x
            if ymax > y:
                ymax = y
            if ymin < y:
                ymin = y
    return xmax, xmin, ymax, ymin

def get4extrems(G, floyd_weight):
    xmax, xmin, ymax, ymin = get_extremums(G, floyd_weight)
    center = find_center(G, floyd_weight)
    a = find_node_by_pos(G, floyd_weight, (xmax, center[1]))
    b = find_node_by_pos(G, floyd_weight, (xmin, center[1]))
    c = find_node_by_pos(G, floyd_weight, (center[0], ymax))
    d = find_node_by_pos(G, floyd_weight, (center[0], ymin))
    return a, b, c, d

def average_pos(edge):
    xs, ys = zip(*edge['geometry'].coords)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    return (mean_x, mean_y)

def divide_in_four_list(G, dist_floyd, edges, a, b, c, d): #abcd are points ex: 24656676
    res1, res2, res3, res4 = [], [], [], []
    for x, y, n in edges:
        dista = min(dist_floyd[0][x][a], dist_floyd[0][y][a])
        distb = min(dist_floyd[0][x][b], dist_floyd[0][y][b])
        distc = min(dist_floyd[0][x][c], dist_floyd[0][y][c])
        distd = min(dist_floyd[0][x][d], dist_floyd[0][y][d])
        best = min(dista, distb, distc, distd)
        if (best == dista):
            res1.append((x,y,n))
        elif (best == distb):
            res2.append((x,y,n))
        elif (best == distc):
            res3.append((x,y,n))
        else:
            res4.append((x,y,n))
    return (res1, res2, res3, res4)

def remove_bad_edges(G, floyd_results, edges):
    def accessibility_heuristic(edge, curr_pos):
        return floyd_results[0][curr_pos][edge[0]] == float("inf") or floyd_results[0][curr_pos][edge[0]] == float("inf")
    def count_inaccessibility(edge):
        return sum([accessibility_heuristic(edge, pos) for pos in G.nodes()])
    def edge_condition(edge):
        return count_inaccessibility(edge) <= len(G.nodes()) / 100
    return list(filter(edge_condition, edges))


def charues_stat(nb_km):
    """
    Calcule et affiche les coûts pour les deux types de déneigeuses

    Pramètres :
        - nb_km : nombre de kilomètres (int)
    
    Retour : None
    """
    print("\nPour une deneigeuse de type I :")
    charue_stat(nb_km,10,1.1,500)
    print("\nPour une deneigeuse de type II :")
    charue_stat(nb_km,20,1.3,800)


def divide_list(l):
    return l[:len(l)//2], l[len(l)//2:]


def one_charrue(G, floyd_results, snow_edges):
    """
    distance totale
    cout total
    temps pour déneiger
    """
    starting_node = None
    for i in G.nodes():
        starting_node = i 
    snow_edges = remove_bad_edges(G, floyd_results, snow_edges)
    
    path_charue1 = getPaths(G, floyd_results, snow_edges, starting_node)

    return get_total_dist(G, path_charue1) / 1000


def four_charrues(G, floyd_results, snow_edges):
    """
    distance totale
    cout total
    temps pour déneiger
    """

    snow_edges = remove_bad_edges(G, floyd_results, snow_edges)
    a,b,c,d = get4extrems(G, floyd_results[0])
    path1, path2, path3, path4 = divide_in_four_list(G, floyd_results, copy.deepcopy(snow_edges), a, b, c, d)
    middle1 = nearest_node(G, find_center(G, floyd_results))
    #middle2 = get_starting_point(G, floyd_results)
    path_charue1 = getPaths(G, floyd_results, path1, middle1)
    path_charue2 = getPaths(G, floyd_results, path2, middle1)
    path_charue3 = getPaths(G, floyd_results, path3, middle1)
    path_charue4 = getPaths(G, floyd_results, path4, middle1)
    dist_1 = get_total_dist(G, path_charue1) / 1000
    dist_2 = get_total_dist(G, path_charue2) / 1000
    dist_3 = get_total_dist(G, path_charue3) / 1000
    dist_4 = get_total_dist(G, path_charue4) / 1000
    return dist_1, dist_2, dist_3, dist_4

def scenario(G, G_aug, quartier, p):
    """
    Simule un scénario pour les deux types de déneigeuses

    Pramètres :
        - G : Le graphe (Graphe)
        - G_aug : Version eulerianizée du graphe (Graphe)
        - quartier : Le nom du quartier (string)
        - p : La probabilité d'enneiger une arête (float)
    
    Retour : None
    """
    # print
    print("")
    #with open("./database/maps/" + quartier.replace(" ", "-") + ".gpickle", 'rb') as f:
    #    G = pickle.load(f).to_directed()
    # enneiger

    G = snowize(G, p)
    G_bis = nx.MultiGraph(G)

    # listes des aretes enneigees
    snow_edges = snow_roads(G_aug, G_bis)
    
    ## Deneigeuse
    fix_edges(G, snow_edges)

    floyd_results = load_floyd_warshall(quartier)

    
    d1, d2, d3, d4 = four_charrues(G, floyd_results, snow_edges)
    #charue_stat(nb_km,10,1.1,500)

    cout1, temps1 = charue_stat(d1,20,1.3,800)
    cout2, temps2 = charue_stat(d2,20,1.3,800)
    cout3, temps3 = charue_stat(d3,20,1.3,800)
    cout4, temps4 = charue_stat(d4,20,1.3,800)

    minTime = min(temps1, temps2, temps3, temps4)
    nb_h = math.floor(minTime)
    nb_minutes = round((minTime - nb_h) * 60)


    print("\n== Le scénario le plus rapide utilise 4 déneigeuses de type II ==")
    print("Distance totale :", round(d1 + d2 + d3 + d4, 2), "km.")
    print("Coût total :", round(cout1 + cout2 + cout3 + cout4, 2), "€.")
    print("Le quartier est déneigé en", nb_h, "h et", nb_minutes, "minutes.")

    d5 = one_charrue(G, floyd_results, snow_edges)
    cout5, temps5 = charue_stat(d5,10,1.1,500)
    cout6, temps6 = charue_stat(d5, 20, 1.3, 800)
    
    nb_h5 = math.floor(temps5)
    nb_minutes5 = round((temps5 - nb_h5) * 60)

    nb_h6 = math.floor(temps6)
    nb_minutes6 = round((temps6 - nb_h6) * 60)

    print("\n== Le scénario qui utilise le moins de déneigeuses ==")
    print("Coût total :", round(cout5, 2), "€ avec 1 déneigeuse de type I et", round(cout6, 2), "€ avec 1 déneigeuse de type II.")
    print("Le quartier est déneigé en", nb_h5, "h et", nb_minutes5, "minutes avec la déneigeuse de type I et en", nb_h6, "h et", nb_minutes6, "minutes avec la déneigeuse de type II.")
    print("Distance totale :", round(d5, 2), "km.")


    print("\n== Le scénario le plus économe ==")

    cout1, temps1 = charue_stat(d1,10,1.1,500)
    cout2, temps2 = charue_stat(d2,10,1.1,500)
    cout3, temps3 = charue_stat(d3,10,1.1,500)
    cout4, temps4 = charue_stat(d4,10,1.1,500)

    if (d5 < d1 + d2 + d3 + d4):
        if (cout5 < cout6):
            print("Coût total :", round(cout5, 2), "€ avec 1 déneigeuse de type I")
            print("Le quartier est déneigé en", nb_h5, "h et", nb_minutes5, "minutes.")
        else:
            print("Coût total :", round(cout6, 2), "€ avec 1 déneigeuse de type II")
            print("Le quartier est déneigé en", nb_h6, "h et", nb_minutes6, "minutes.")
        print("Distance totale :", round(d5, 2), "km.")
    elif (cout5 < cout1 + cout2 + cout3 + cout4):
        print("Coût total :", round(cout5, 2), "€ avec 1 déneigeuse de type I")
        print("Le quartier est déneigé en", nb_h5, "h et", nb_minutes5, "minutes.")
        print("Distance totale :", round(d5, 2), "km.")
    else:
        minTime = min(temps1, temps2, temps3, temps4)
        nb_h = math.floor(minTime)
        nb_minutes = round((minTime - nb_h) * 60)
        print("Coût total :", round(cout1 + cout2 + cout3 + cout4, 2), "€ avec 4 déneigeuses de type I")
        print("Le quartier est déneigé en", nb_h, "h et", nb_minutes, "minutes.")
        print("Distance totale :", round(d1 + d2 + d3 + d4, 2), "km.")
    
def main():
    ## Intro
    print("================ ERO1 ================")
    for i in range(len(quartiers)):
        print(f"{i+1}) {quartiers[i]}")
    print("")
    res = int(input("Choisissez une quartier (ex: 1, 2 ...): "))
    quartier = quartiers[res-1]

    ## Drone
    # import des G
    G = import_G("./database/maps/" + quartier.replace(" ", "-") + ".gpickle")
    G_aug = import_G("./database/eulerized_maps/" + quartier.replace(" ", "-") + "_aug.gpickle")
    G_bis = nx.MultiGraph(G)

    # circuit eulerien
    cir = circuit(G_aug)

    # print 
    sum_graph = sum_dist(G)
    print("La somme des distances des routes du quartier est de ", str(round(sum_graph/1000,2)), " km.") 
    
    sum_circuit = sum_dist_circuit(G_bis, cir)

    km = sum_circuit/1000
    cout = km/100
    print("=== Drone ===")
    print("La distance parcourue par le drone est de " + str(round(km, 2)) + " km.")
    print("Alors, le cout du drone est de " + str(round(cout, 2) + 100) + " €.")
    
    scenario(G, G_aug, quartier, 0.3)
    #scenario(G, G_aug, quartier, 0.5)
    #scenario(G, G_aug, quartier, 0.9)

main()
