import numpy as np
import matplotlib.pyplot as plt
import re
import tkinter as tk
from tkinter import simpledialog
from matplotlib.animation import FuncAnimation

# Constante gravitationnelle (en km^3 kg^(-1) s^(-2))
G = 6.67430e-20  # Convertie en km^3/kg/s^2
M_SOLEIL = 1.989e30  # Masse du Soleil en kg

# Fonction pour convertir l'entrée de l'utilisateur en un nombre flottant interprétant la notation scientifique
def convertir_entree_scientifique(entree):
    entree = re.sub(r'[×x]\s*10\^?', 'e', entree)  # Remplace '× 10^' par 'e'
    try:
        return float(entree)
    except ValueError:
        raise ValueError(f"Impossible de convertir l'entrée '{entree}' en nombre.")

# Classe pour représenter un objet céleste
class Corps:
    def __init__(self, nom, masse, position, vitesse):
        self.nom = nom
        self.masse = masse
        self.position = np.array(position, dtype='float64')
        self.vitesse = np.array(vitesse, dtype='float64')
        self.force = np.array([0.0, 0.0], dtype='float64')

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

# Fonction pour calculer la distance au Soleil en fonction de la période orbitale
def calculer_distance_orbitale(periode_orbitale_jours):
    periode_orbitale_secondes = periode_orbitale_jours * 24 * 3600
    distance_orbitale_km = (G * M_SOLEIL * (periode_orbitale_secondes**2) / (4 * np.pi**2))**(1/3)
    return distance_orbitale_km

# Fonction pour calculer la vitesse orbitale circulaire
def calculer_vitesse_orbitale(distance_orbitale_km):
    return np.sqrt(G * M_SOLEIL / distance_orbitale_km)

# Fonction pour entrer les données manuellement via Tkinter
def entrer_corps():
    nom = simpledialog.askstring("Input", "Entrez le nom de la planète :")
    if not nom:
        return None
    
    masse_str = simpledialog.askstring("Input", f"Entrez la masse de {nom} (ex: 5,972 × 10^24 kg) :")
    if not masse_str:
        return None
    masse = convertir_entree_scientifique(masse_str)
    
    periode_orbitale_jours_str = simpledialog.askstring("Input", f"Entrez la période orbitale de {nom} (en jours) :")
    if not periode_orbitale_jours_str:
        return None
    periode_orbitale_jours = float(periode_orbitale_jours_str)
    
    # Calculer la distance orbitale et la vitesse correspondante
    distance_orbitale_km = calculer_distance_orbitale(periode_orbitale_jours)
    vitesse_orbitale_kms = calculer_vitesse_orbitale(distance_orbitale_km)
    
    # On suppose que la planète commence à (distance_orbitale, 0) et que sa vitesse est perpendiculaire
    position = [distance_orbitale_km, 0]
    vitesse = [0, vitesse_orbitale_kms]
    
    return Corps(nom, masse, position, vitesse)

# Fonction principale pour exécuter la simulation
def run_simulation():
    corps_celestes = []
    nombre_corps = simpledialog.askinteger("Input", "Combien de planètes voulez-vous ajouter (hors Soleil) ?")

    # Soleil
    soleil = Corps("Soleil", masse=M_SOLEIL, position=[0, 0], vitesse=[0, 0])
    corps_celestes.append(soleil)

    # Ajouter les planètes
    for _ in range(nombre_corps):
        corps = entrer_corps()
        if corps:
            corps_celestes.append(corps)

    # Paramètres de la simulation
    dt = 432000  # Pas de temps (5 jours)
    total_steps = int((12 * 365 * 24 * 3600) // dt)  # Simulation pour 12 ans
    positions = {corps.nom: [] for corps in corps_celestes}

    # Initialiser les données pour le tableau
    vitesse_moyenne = {corps.nom: {20: None, 250: None} for corps in corps_celestes if corps.nom != "Soleil"}
    force_moyenne = {corps.nom: {20: None, 250: None} for corps in corps_celestes if corps.nom != "Soleil"}

    # Tracer des trajectoires avec animation
    fig, ax = plt.subplots(figsize=(16, 9))  # Adapter la taille de la figure pour 1920x1080
    ax.set_xlim(-1.5e9, 1.5e9)  # Limites x en km
    ax.set_ylim(-1.5e9, 1.5e9)  # Limites y en km
    ax.set_title('Simulation du système solaire avec trajectoires animées')
    ax.set_xlabel('Position X (km)')
    ax.set_ylabel('Position Y (km)')
    ax.grid()

    # Initialiser les graphiques pour les corps célestes
    scatters = {corps.nom: ax.plot([], [], 'o-', label=corps.nom, markersize=4)[0] for corps in corps_celestes if corps.nom != "Soleil"}
    ax.scatter([0], [0], color='yellow', edgecolor='black', s=300, label='Soleil')

    plt.legend()

    # Fonction d'initialisation pour l'animation
    def init():
        for scatter in scatters.values():
            scatter.set_data([], [])
        return scatters.values()

    # Fonction d'animation
    def update(frame):
        # Mettre à jour les forces et les positions de chaque corps céleste
        for corps in corps_celestes:
            corps.maj_force(corps_celestes)
            corps.maj_position_et_vitesse(dt)
            positions[corps.nom].append(corps.position.copy())  # Enregistrer la position

            # Enregistrer les valeurs si le temps courant est proche des moments d'intérêt
            temps_courant = frame * dt
            if corps.nom != "Soleil":
                if temps_courant == 20 * 24 * 3600:
                    vitesse_moyenne[corps.nom][20] = np.linalg.norm(corps.vitesse)
                    force_moyenne[corps.nom][20] = np.linalg.norm(corps.force)

                if temps_courant == 250 * 24 * 3600:
                    vitesse_moyenne[corps.nom][250] = np.linalg.norm(corps.vitesse)
                    force_moyenne[corps.nom][250] = np.linalg.norm(corps.force)

        # Mettre à jour les positions des corps célestes pour l'animation
        for corps in corps_celestes:
            if corps.nom != "Soleil":
                positions_arr = np.array(positions[corps.nom])
                scatters[corps.nom].set_data(positions_arr[:, 0], positions_arr[:, 1])

        return scatters.values()

    # Créer l'animation
    ani = FuncAnimation(fig, update, frames=total_steps, init_func=init, blit=True, repeat=False)

    plt.show()

    # Afficher le tableau des valeurs
    afficher_tableau(vitesse_moyenne, force_moyenne)

# Fonction pour afficher le tableau des valeurs
def afficher_tableau(vitesse_moyenne, force_moyenne):
    fig_tableau = plt.figure(figsize=(16, 6))  # Taille de la figure ajustée pour le tableau
    table_data = []
    headers = ["Corps", "Vitesse à 20 jours (km/s)", "Force à 20 jours (N)", "Vitesse à 250 jours (km/s)", "Force à 250 jours (N)"]
    table_data.append(headers)

    # Remplir les données du tableau
    for corps in vitesse_moyenne.keys():
        v_20 = vitesse_moyenne[corps][20]
        f_20 = force_moyenne[corps][20]
        v_250 = vitesse_moyenne[corps][250]
        f_250 = force_moyenne[corps][250]
        table_data.append([corps, v_20, f_20, v_250, f_250])

    # Créer le tableau
    plt.table(cellText=table_data, cellLoc='center', loc='center')
    plt.axis('off')  # Cacher les axes
    plt.title("Tableau des vitesses et forces à 20 et 250 jours")
    plt.show()

# Créer la fenêtre principale
root = tk.Tk()
root.withdraw()  # Cacher la fenêtre principale

# Lancer la simulation
run_simulation()

# Fermer l'application après la simulation
root.destroy()
