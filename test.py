import numpy as np
import matplotlib.pyplot as plt
import re
import tkinter as tk
from tkinter import simpledialog, messagebox

# Constante gravitationnelle (en km^3 kg^(-1) s^(-2))
G = 6.67430e-20  # Convertie en km^3/kg/s^2
M_SOLEIL = 1.989e30  # Masse du Soleil en kg

# Fonction pour convertir l'entrée de l'utilisateur en un nombre flottant interprétant la notation scientifique
def convertir_entree_scientifique(entree):
    # Remplacer les variantes de notation comme "× 10^" par "e"
    entree = re.sub(r'[×x]\s*10\^?', 'e', entree)  # Remplace '× 10^' par 'e'
    try:
        return float(entree)
    except ValueError:
        raise ValueError(f"Impossible de convertir l'entrée '{entree}' en nombre.")

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

# Fonction pour calculer la distance au Soleil en fonction de la période orbitale
def calculer_distance_orbitale(periode_orbitale_jours):
    periode_orbitale_secondes = periode_orbitale_jours * 24 * 3600
    # En utilisant la 3e loi de Kepler pour les orbites circulaires
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
    
    temps_simulation = periode_orbitale_jours * 24 * 3600  # Conversion de la période en secondes

    return Corps(nom, masse, position, vitesse, periode_orbitale_jours * 24 * 3600, temps_simulation)

# Fonction principale pour exécuter la simulation
def run_simulation():
    corps_celestes = []
    nombre_corps = simpledialog.askinteger("Input", "Combien de planètes voulez-vous ajouter (hors Soleil) ?")

    # Soleil
    soleil = Corps("Soleil", masse=1.989e30, position=[0, 0], vitesse=[0, 0], periode_orbitale=np.inf, temps_de_simulation=np.inf)
    corps_celestes.append(soleil)

    # Ajouter les planètes
    for _ in range(nombre_corps):
        corps = entrer_corps()
        if corps:
            corps_celestes.append(corps)

    # Paramètres de la simulation
    dt = 3600  # Pas de temps (1 heure)
    intervalle_enregistrement = 24  # Enregistrer les positions tous les 24 heures

    # Stocker les positions pour tracer
    positions = {corps.nom: [] for corps in corps_celestes}
    vitesse_moyenne = {corps.nom: {20: None, 250: None} for corps in corps_celestes if corps.nom != "Soleil"}
    force_moyenne = {corps.nom: {20: None, 250: None} for corps in corps_celestes if corps.nom != "Soleil"}

    # Boucle de simulation
    for step in range(int((12 * 365 * 24 * 3600) // dt)):  # Simulation pour un maximum de 12 ans
        for corps in corps_celestes:
            corps.maj_force(corps_celestes)

        for corps in corps_celestes:
            corps.maj_position_et_vitesse(dt)

            # Enregistrer les positions
            if step % (intervalle_enregistrement) == 0:
                positions[corps.nom].append(corps.position.copy())

            # Enregistrer les valeurs si le temps courant est proche des moments d'intérêt
            temps_courant = step * dt
            if corps.nom != "Soleil":
                if temps_courant == 20 * 24 * 3600:
                    vitesse_moyenne[corps.nom][20] = np.linalg.norm(corps.vitesse)
                    force_moyenne[corps.nom][20] = np.linalg.norm(corps.force)

                if temps_courant == 250 * 24 * 3600:
                    vitesse_moyenne[corps.nom][250] = np.linalg.norm(corps.vitesse)
                    force_moyenne[corps.nom][250] = np.linalg.norm(corps.force)

    # Tracer des trajectoires
    plt.figure(figsize=(12, 6))

    for corps in corps_celestes:
        if corps.nom != "Soleil":
            positions_arr = np.array(positions[corps.nom])
            plt.plot(positions_arr[:, 0] / 1e6, positions_arr[:, 1] / 1e6, 'o-', label=corps.nom, markersize=4)

    plt.scatter([0], [0], color='yellow', edgecolor='black', s=300, label='Soleil')
    plt.legend()
    plt.title('Simulation du système solaire simplifié avec trajectoires')
    plt.xlabel('Position X (millions de km)')
    plt.ylabel('Position Y (millions de km)')
    plt.grid()

    plt.show()

    # Tableau des valeurs à t = 20 jours et t = 250 jours
    fig_tableau = plt.figure(figsize=(14, 7))  # Taille de la figure ajustée
    table_data = []
    headers = ["Corps", "Vitesse à 20 jours (km/s)", "Force à 20 jours (N)", "Vitesse à 250 jours (km/s)", "Force à 250 jours (N)"]
    table_data.append(headers)

    for corps in corps_celestes:
        if corps.nom != "Soleil":
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

    # Créer le tableau
    table = plt.table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.2, 0.2, 0.25, 0.2, 0.25])
    table.auto_set_font_size(False)
    table.set_fontsize(12)  # Ajuster la taille de la police si nécessaire
    table.scale(1.3, 1.3)  # Ajuster l'échelle pour mieux utiliser l'espace (ajouter un peu plus d'espace)

    plt.axis('off')  # Ne pas afficher les axes
    plt.show()

# Créer la fenêtre principale
root = tk.Tk()
root.withdraw()  # Cacher la fenêtre principale

# Lancer la simulation
run_simulation()

# Fermer l'application après la simulation
root.destroy()
