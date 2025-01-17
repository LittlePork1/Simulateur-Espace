# Simulateur-Espace
Simulateur espace pour projet expérimental / ESAIP ING2

Ce projet est une simulation interactive du système solaire, permettant de visualiser les trajectoires de planètes autour du Soleil. La simulation prend en compte les forces gravitationnelles pour calculer les positions et vitesses des corps célestes en fonction du temps.
Fonctionnalités

    Ajout dynamique de planètes :
        L'utilisateur peut ajouter plusieurs planètes au système solaire via des boîtes de dialogue interactives (Tkinter).
        Chaque planète est définie par son nom, sa masse, et sa période orbitale.
        La distance orbitale et la vitesse initiale sont calculées automatiquement à partir des données fournies.

    Images et textures :
        Les planètes et le Soleil sont représentés par des images personnalisées (issues du dossier textures).
        Une image de fond est utilisée pour un rendu esthétique de la simulation.

    Simulation des trajectoires :
        Les trajectoires des planètes sont calculées en tenant compte des forces gravitationnelles entre les corps célestes.
        Les positions et vitesses sont mises à jour à chaque étape de simulation.

    Animation dynamique :
        Une animation est générée pour visualiser le mouvement des planètes en temps réel.
        Les positions des corps célestes sont représentées à l'échelle, avec des icônes ajustées.

    Affichage des données des corps célestes :
        Les informations sur les corps (nom, masse, position, vitesse, distance au Soleil) sont présentées dans un tableau interactif.

Prérequis

Pour exécuter ce projet, vous devez avoir installé les bibliothèques suivantes :

    numpy : pour les calculs mathématiques et les vecteurs.
    matplotlib : pour les graphiques et l'animation.
    Pillow : pour manipuler les images.
    tkinter : pour les boîtes de dialogue interactives.
    pandas : pour organiser et afficher les données dans un tableau.

Pour installer les dépendances manquantes, utilisez :

pip install numpy matplotlib pillow pandas

Fichiers du projet

    main.py : le script principal contenant toute la logique de simulation.
    textures/ : un dossier contenant les images utilisées pour représenter les planètes, le Soleil et l'arrière-plan.

Utilisation

    Exécution du script : Lancez le script Python via votre terminal ou IDE préféré :

    python main.py

    Interaction utilisateur :
        Une boîte de dialogue vous demande combien de planètes ajouter.
        Entrez les informations pour chaque planète (nom, masse, période orbitale).
        La simulation commence une fois toutes les données saisies.

    Visualisation :
        Regardez les planètes évoluer dans leur trajectoire.
        Les trajectoires et positions sont recalculées dynamiquement en fonction des lois de la gravité.

    Affichage des données :
        À la fin de la simulation, un tableau récapitule les informations sur les planètes (masse, position, vitesse, distance au Soleil).

Détails techniques
Calculs scientifiques

    Distance orbitale :
    La distance orbitale est calculée à partir de la période orbitale donnée par l'utilisateur, en utilisant la troisième loi de Kepler :
    R=(G⋅Msoleil⋅T24π2)1/3
    R=(4π2G⋅Msoleil​⋅T2​)1/3

    Où :
        GG : constante gravitationnelle.
        MsoleilMsoleil​ : masse du Soleil.
        TT : période orbitale en secondes.

    Vitesse orbitale :
    La vitesse initiale d'une planète est calculée pour une orbite circulaire à partir de la formule :
    v=G⋅MsoleilR
    v=RG⋅Msoleil​​

    ​

    Mise à jour des positions et vitesses :
    Les forces gravitationnelles sont calculées pour chaque paire de corps célestes, et les positions/vitesses sont mises à jour via les équations de mouvement :
    F=G⋅m1⋅m2r2
    F=G⋅r2m1​⋅m2​​

    Où rr est la distance entre deux corps célestes.

Interface utilisateur

    Tkinter est utilisé pour les boîtes de dialogue interactives.
    Les positions des corps célestes sont affichées via matplotlib.

Animation

    L'animation est gérée via FuncAnimation de matplotlib.
    Les images des planètes sont placées dynamiquement sur la carte via OffsetImage et AnnotationBbox.

Résultats attendus

    Une simulation visuelle des orbites des planètes autour du Soleil.
    Un tableau des données des corps célestes à la fin de la simulation.

Vous pouvez personnaliser les textures en remplaçant les images dans le dossier textures ou ajuster les paramètres de simulation (comme le pas de temps dt).
