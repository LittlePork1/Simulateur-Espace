import numpy as np
import matplotlib.pyplot as plt

# Constante gravitationnelle (en km^3 kg^(-1) s^(-2))
G = 6.67430e-20  # Convertie en km^3/kg/s^2

# Classe pour représenter un objet céleste
class Corps:
    def __init__(self, nom, masse, position, vitesse, periode_orbitale, temps_de_simulation):
        self.nom = nom
        self.masse = masse
        self.position = np.array(position, dtype='float64')
        self.vitesse = np.array(vitesse, dtype='float64')
        self.force = np.array([0.0, 0.0], dtype='float64')
        self.periode_orbitale = periode_orbitale  # Période orbitale en secondes
        self.position_initiale = np.array(position)
        self.temps_de_simulation = temps_de_simulation  # Temps de simulation en secondes
        self.temps_ecoule = 0  # Temps écoulé durant la simulation

    def maj_force(self, autres_corps):
        self.force = np.array([0.0, 0.0], dtype='float64')
        
        for autre in autres_corps:
            if autre != self:
                delta_pos = autre.position - self.position
                distance = np.linalg.norm(delta_pos)
                
                if distance == 0:
                    continue

                force_magnitude = G * self.masse * autre.masse / distance**2
                force_direction = delta_pos / distance
                
                self.force += force_magnitude * force_direction

    def maj_position_et_vitesse(self, dt):
        acceleration = self.force / self.masse
        self.vitesse += acceleration * dt
        self.position += self.vitesse * dt
        self.temps_ecoule += dt  # Augmenter le temps écoulé

    def a_retrouve_position_initiale(self):
        return np.allclose(self.position, self.position_initiale, atol=1e5)  # Tolérance pour position initiale

# Créer les corps célestes (Soleil, planètes, etc.)
soleil = Corps("Soleil", masse=1.989e30, position=[0, 0], vitesse=[0, 0], periode_orbitale=np.inf, temps_de_simulation=np.inf)
terre = Corps("Terre", masse=5.972e24, position=[1.496e8, 0], vitesse=[0, 29.78], periode_orbitale=365*24*3600, temps_de_simulation=365*24*3600)  # 1 an
mars = Corps("Mars", masse=6.4171e23, position=[2.279e8, 0], vitesse=[0, 24.077], periode_orbitale=687*24*3600, temps_de_simulation=687*24*3600)  # 687 jours
venus = Corps("Vénus", masse=4.867e24, position=[1.082e8, 0], vitesse=[0, 35.02], periode_orbitale=225*24*3600, temps_de_simulation=225*24*3600)  # 225 jours
jupiter = Corps("Jupiter", masse=1.898e27, position=[7.785e8, 0], vitesse=[0, 13.07], periode_orbitale=4333*24*3600, temps_de_simulation=4333*24*3600)  # 4333 jours

# Liste des corps dans le système
corps_celestes = [soleil, terre, mars, venus, jupiter]

# Paramètres de la simulation
dt = 4 * 3600  # Pas de temps (1 jour)
intervalle_enregistrement = 60  # Enregistrer les positions tous les 120 jours pour réduire les points

# Stocker les positions pour tracer
positions = {corps.nom: [] for corps in corps_celestes}
vitesse_moyenne = {corps.nom: {20: None, 250: None} for corps in corps_celestes if corps.nom != "Soleil"}
force_moyenne = {corps.nom: {20: None, 250: None} for corps in corps_celestes if corps.nom != "Soleil"}

# Boucle de simulation
for step in range(int((12 * 365 * 24 * 3600) // dt)):  # Simulation pour un maximum de 12 ans
    temps_courant = step * dt

    for corps in corps_celestes:
        corps.maj_force(corps_celestes)

    for corps in corps_celestes:
        corps.maj_position_et_vitesse(dt)

        # Enregistrer les positions tous les 120 jours
        if step % (intervalle_enregistrement) == 0:  # Enregistrer toutes les 120 jours
            positions[corps.nom].append(corps.position.copy())

        # Enregistrer les valeurs si le temps courant est proche des moments d'intérêt
        if corps.nom != "Soleil":
            if temps_courant == 20 * 24 * 3600:
                vitesse_moyenne[corps.nom][20] = np.linalg.norm(corps.vitesse)
                force_moyenne[corps.nom][20] = np.linalg.norm(corps.force)

            if temps_courant == 250 * 24 * 3600:
                vitesse_moyenne[corps.nom][250] = np.linalg.norm(corps.vitesse)
                force_moyenne[corps.nom][250] = np.linalg.norm(corps.force)

    # Arrêter la simulation pour Mars après un an
    if mars.temps_ecoule >= mars.temps_de_simulation:  # Si Mars a atteint 687 jours
        mars.position = mars.position_initiale  # Ramener Mars à sa position initiale
        mars.temps_ecoule = 0  # Réinitialiser le temps écoulé pour Mars

# Créer une nouvelle figure pour le graphique
plt.figure(figsize=(12, 6))

# Tracé des trajectoires avec des points espacés
for corps in corps_celestes:
    if corps.nom != "Soleil":  # Pas besoin de tracer l'orbite du Soleil
        positions_arr = np.array(positions[corps.nom])
        plt.plot(positions_arr[:, 0] / 1e6, positions_arr[:, 1] / 1e6, 'o-', label=corps.nom, markersize=4)  # En millions de km

# Tracé du Soleil avec contour pour le rendre plus visible
plt.scatter([0], [0], color='yellow', edgecolor='black', s=300, label='Soleil')
plt.legend()
plt.title('Simulation du système solaire simplifié avec trajectoires')
plt.xlabel('Position X (millions de km)')
plt.ylabel('Position Y (millions de km)')
plt.grid()

# Affichage du graphique
plt.show(block=False)  # Affiche le graphique sans bloquer l'exécution

# Créer une nouvelle figure pour le tableau des valeurs
fig_tableau = plt.figure(figsize=(10, 5))  # Taille ajustée

# Affichage des données à t = 20 jours et t = 250 jours
table_data = []
# Une seule ligne d'en-tête
headers = ["Corps", "Vitesse à 20 jours (km/s)", "Force à 20 jours (N)", "Vitesse à 250 jours (km/s)", "Force à 250 jours (N)"]
table_data.append(headers)

# Préparation des colonnes de données
for corps in corps_celestes:
    if corps.nom != "Soleil":  # Pas besoin d'inclure le Soleil
        v_20 = vitesse_moyenne[corps.nom][20]
        f_20 = force_moyenne[corps.nom][20]
        v_250 = vitesse_moyenne[corps.nom][250]
        f_250 = force_moyenne[corps.nom][250]
        
        table_data.append([
            corps.nom,
            f"{v_20:.2f}" if v_20 is not None else "N/A",
            f"{f_20:.2e}" if f_20 is not None else "N/A",
            f"{v_250:.2f}" if v_250 is not None else "N/A",
            f"{f_250:.2e}" if f_250 is not None else "N/A"
        ])

# Créer un tableau avec matplotlib
table = plt.table(cellText=table_data, colLabels=None, loc='center', cellLoc='center', colWidths=[0.2, 0.2, 0.25, 0.2, 0.25])
table.auto_set_font_size(False)
table.set_fontsize(8)  # Réduire la taille de la police
table.scale(1.2, 1.2)  # Réduire l'échelle du tableau pour mieux s'adapter
plt.axis('off')

# Affichage du tableau
plt.show(block=False)  # Affiche le tableau sans bloquer l'exécution

# Garder le script en cours d'exécution pour voir les fenêtres
input("Appuyez sur Entrée pour fermer les fenêtres...")
