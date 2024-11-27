#IMPORTATION DES BIBLIOTHEQUES
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.animation import FuncAnimation
import re
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageOps

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
    def __init__(self, nom, masse, position, vitesse, couleur, texture=None):
        self.nom = nom
        self.masse = masse
        self.position = np.array(position, dtype='float64')
        self.vitesse = np.array(vitesse, dtype='float64')
        self.force = np.array([0.0, 0.0], dtype='float64')
        self.couleur = couleur
        self.texture = texture  # Image de texture si disponible

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

# Fonction pour calculer la distance orbitale en fonction de la période orbitale
def calculer_distance_orbitale(periode_orbitale_jours):
    periode_orbitale_secondes = periode_orbitale_jours * 24 * 3600
    distance_orbitale_km = (G * M_SOLEIL * (periode_orbitale_secondes**2) / (4 * np.pi**2))**(1/3)
    return distance_orbitale_km

# Fonction pour calculer la vitesse orbitale circulaire
def calculer_vitesse_orbitale(distance_orbitale_km):
    return np.sqrt(G * M_SOLEIL / distance_orbitale_km)

# Chargement des textures
def charger_texture(chemin, taille):
    image = Image.open(chemin)
    image = ImageOps.fit(image, (taille, taille), Image.ANTIALIAS)
    return np.array(image)

# Fonction pour entrer les données via Tkinter
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
    distance_orbitale_km = calculer_distance_orbitale(periode_orbitale_jours)
    vitesse_orbitale_kms = calculer_vitesse_orbitale(distance_orbitale_km)
    position = [distance_orbitale_km, 0]
    vitesse = [0, vitesse_orbitale_kms]
    couleur = simpledialog.askstring("Input", f"Entrez une couleur pour {nom} (ex: 'blue', 'green', etc.) :")
    return Corps(nom, masse, position, vitesse, couleur)

# Fonction principale pour la simulation
def run_simulation():
    corps_celestes = []
    nombre_corps = simpledialog.askinteger("Input", "Combien de planètes voulez-vous ajouter (hors Soleil) ?")

    # Soleil
    soleil_texture = charger_texture("textures/soleil.png", 300)
    soleil = Corps("Soleil", masse=M_SOLEIL, position=[0, 0], vitesse=[0, 0], couleur='yellow', texture=soleil_texture)
    corps_celestes.append(soleil)

    for _ in range(nombre_corps):
        corps = entrer_corps()
        if corps:
            corps_celestes.append(corps)

    # Simulation
    dt = 432000  # Pas de temps (5 jours)
    total_steps = 500
    positions = {corps.nom: [] for corps in corps_celestes}

    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_xlim(-1.5e9, 1.5e9)
    ax.set_ylim(-1.5e9, 1.5e9)
    ax.set_title("Simulation du Système Solaire", fontsize=16)
    ax.set_xlabel("Position X (km)", fontsize=12)
    ax.set_ylabel("Position Y (km)", fontsize=12)
    ax.grid()

    # Halo du Soleil
    ax.add_artist(Circle((0, 0), 1e8, color='yellow', alpha=0.3))

    # Animations
    def init():
        for corps in corps_celestes:
            if corps.texture is not None:
                ax.imshow(corps.texture, extent=(-1e8, 1e8, -1e8, 1e8))
        return []

    def update(frame):
        for corps in corps_celestes:
            corps.maj_force(corps_celestes)
            corps.maj_position_et_vitesse(dt)
            positions[corps.nom].append(corps.position.copy())
        ax.clear()
        for corps in corps_celestes:
            ax.scatter(corps.position[0], corps.position[1], color=corps.couleur, s=50)
        return []

    ani = FuncAnimation(fig, update, frames=total_steps, init_func=init, blit=False, repeat=False)
    plt.show()

# Créer la fenêtre Tkinter
root = tk.Tk()
root.withdraw()

# Lancer la simulation
run_simulation()

# Quitter
root.destroy()
