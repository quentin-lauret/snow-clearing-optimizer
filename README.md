# ERO1


## Structure du projet :
### Le dossier database :
Le dossier database contient l'ensemble des données utiles à l'exécution des programmes du projet. En voici un descriptif :
 - maps : contient les données de tous les quartiers de Montréal et de la ville en entier sous forme de graphes
 - eulerized_maps : contient l'ensemble des graphes précédemment cités en version eulérienne

### Le dossier déneigeuses :
Le dossier déneigeuses contient les fichiers jupyter qui retracent notre travail et nos différentes pistes de recherche au sujet des déneigeuses.

### Le dossier drone :
Le dossier drone contient les fichiers jupyter qui retracent notre travail et nos différentes pistes de recherche au sujet des drones.

### ERO1.ipynb :
Ce fichier contient une synthèse de notre travail qui permet de lancer la simulation des drones et des déneigeuses. Il contient aussi des animations permettant de visualiser le chemin des différents véhicules. 

### ero1.py:
Ce fichier sert à tester plusieurs scénarios avec des proportions de neige différentes et avec un nombre variable de déneigeuses

### animations:
Contient plusieurs animations des déneigeuses et du drone :
- circuit_montreal_fast : parcours du drone
- plateau_mr_4 : parcours des déneigeuses

## Installation :
Exécuter la commande ```./install.sh```

## Lancement de la simulation pour plusieurs scénarios :
Exécuter la commande ```python3 ero1.py```

## Lancement des animations :
- Exécuter la commande ```jupyter lab```
- Ouvrir le fichier ERO1.ipynb
- Exécuter toutes les cellules (en changeant éventuellement le nom du quartier dans la dernière cellule)



# PLEASE READ ME

Scénarios pour la charrue:
- Calcul d'un seul itinéraire
    - Une seule charrue utilisée (2 possibilités)
    - Deux charues partent du centre (4 possibilités)
- Calcul de plusieurs itinéraires
    - Une seule charrue par sous-itinéraire
    - Deux charues partent du centre
    - Deux charues partent du centre des trajets les plus longs
    - (On peut ne traite pas les quartiers avec moins d'un certain nombre de rues enneigées)

- Point de départ aléatoire
- Point de départ au centre calculé géographiquement
- Point de départ au centre calculé avec Floyd-Warshall
