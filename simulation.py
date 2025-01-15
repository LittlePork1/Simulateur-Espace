import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.animation import FuncAnimation
from tkinter import Tk, simpledialog
import re
from matplotlib.offsetbox import OffsetImage, AnnotationBbox  # Pour afficher les images sur la carte
from tableau import afficher_tableau

# Constante gravitationnelle (en km^3 kg^(-1) s^(-2))
G = 6.67430e-20  # Constante gravitationnelle en km^3/kg/s^2

# Dictionnaire des chemins d'image
images = {
    "Soleil": 'textures/soleil.png',  # Chemin relatif vers l'image du Soleil
    "Terre": 'textures/earth.png',  # Exemple pour la Terre
    "Mars": 'textures/mars.png',
    "Mercure": 'textures/mercure.png',
    "Jupiter": 'textures/jupiter.png',
    "Uranus": 'textures/uranus.png',
    "background": 'textures/background.jpg',  # Image de fond
}

# Fonction pour convertir l'entrée de l'utilisateur en un nombre flottant
def convertir_entree_scientifique(entree):
    entree = re.sub(r'[×x]\s*10\^?', 'e', entree)  # Remplace 's× 10^' par 'e'
    try:
        return float(entree)
    except ValueError:
        raise ValueError(f"Impossible de convertir l'entrée '{entree}' en nombre.")

# Classe pour représenter un objet céleste
class Corps:
    def __init__(self, nom, masse, position, vitesse, image_path=None):
        self.nom = nom
        self.masse = masse
        self.position = np.array(position, dtype='float64')
        self.vitesse = np.array(vitesse, dtype='float64')
        self.force = np.array([0.0, 0.0], dtype='float64')
        
        # Si une image est fournie, charger l'image
        if image_path:
            self.image = Image.open(image_path)
            self.image.thumbnail((50, 50))  # Réduire la taille de l'image pour l'affichage
            self.offset_image = OffsetImage(self.image, zoom=0.1)  # Ajuster la taille de l'image
        else:
            self.image = None
            self.offset_image = None

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
def calculer_distance_orbitale(periode_orbitale_jours, masse_soleil):
    periode_orbitale_secondes = periode_orbitale_jours * 24 * 3600
    distance_orbitale_km = (G * masse_soleil * (periode_orbitale_secondes**2) / (4 * np.pi**2))**(1/3)
    return distance_orbitale_km

# Fonction pour calculer la vitesse orbitale circulaire
def calculer_vitesse_orbitale(distance_orbitale_km, masse_soleil):
    return np.sqrt(G * masse_soleil / distance_orbitale_km)

# Fonction pour entrer les données manuellement via Tkinter
def entrer_corps(masse_soleil):
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
    distance_orbitale_km = calculer_distance_orbitale(periode_orbitale_jours, masse_soleil)
    vitesse_orbitale_kms = calculer_vitesse_orbitale(distance_orbitale_km, masse_soleil)
    
    # On suppose que la planète commence à (distance_orbitale, 0) et que sa vitesse est perpendiculaire
    position = [distance_orbitale_km, 0]
    vitesse = [0, vitesse_orbitale_kms]

    # Vérifier si l'image existe pour la planète
    image_path = images.get(nom, None)
    
    return Corps(nom, masse, position, vitesse, image_path)

# Fonction principale pour exécuter la simulation
def run_simulation():
    corps_celestes = []
    nombre_corps = simpledialog.askinteger("Input", "Combien de planètes voulez-vous ajouter (hors Soleil) ?")

    # Demander la masse du Soleil à l'utilisateur
    masse_soleil_str = simpledialog.askstring("Input", "Entrez la masse du Soleil (ex: 1,989 × 10^30 kg) :")
    if not masse_soleil_str:
        return
    masse_soleil = convertir_entree_scientifique(masse_soleil_str)

    # Soleil (avec masse dynamique et image)
    soleil = Corps("Soleil", masse=masse_soleil, position=[0, 0], vitesse=[0, 0], image_path=images["Soleil"])
    corps_celestes.append(soleil)

    # Ajouter les planètes
    distances = []  # Stocker les distances orbitale pour ajuster les limites de l'axe
    for _ in range(nombre_corps):
        corps = entrer_corps(masse_soleil)  # Passez masse_soleil ici
        if corps:
            corps_celestes.append(corps)
            distance = np.linalg.norm(corps.position)  # Distance orbitale initiale
            distances.append(distance)

    # Trouver la distance orbitale maximale
    distance_max = max(distances) if distances else 1e8  # Valeur par défaut si aucune planète

    # Ajuster les limites dynamiquement avec une marge
    marge = 1.2  # Marge de 20% pour ne pas coller les bords
    xlim = ylim = distance_max * marge

    # Paramètres de la simulation
    dt = 432000  # Pas de temps (5 jours)
    total_steps = int((12 * 365 * 24 * 3600) // dt)  # Simulation pour 12 ans
    positions = {corps.nom: [] for corps in corps_celestes}

    # Tracer des trajectoires avec animation
    fig, ax = plt.subplots(figsize=(16, 9))  # Adapter la taille de la figure pour 1920x1080
    ax.set_xlim(-xlim, xlim)  # Limites x dynamiques
    ax.set_ylim(-ylim, ylim)  # Limites y dynamiques

    # Charger l'image de fond
    background_img = Image.open(images["background"])
    ax.imshow(background_img, extent=[-xlim, xlim, -ylim, ylim], aspect='auto')

    # Enlever le quadrillage
    ax.grid(False)

    ax.set_title('Simulation du système solaire avec trajectoires animées')
    ax.set_xlabel('Position X (km)')
    ax.set_ylabel('Position Y (km)')
    
    plt.legend()

    # Initialiser les graphiques pour les corps célestes
    scatters = {corps.nom: ax.plot([], [], 'o-', label=corps.nom, markersize=4)[0] for corps in corps_celestes if corps.nom != "Soleil"}
    ax.scatter([0], [0], color='yellow', edgecolor='black', s=300, label='Soleil')

    # Ajuster la taille de l'image du Soleil
    zoom_soleil = 200 / 195
    soleil.offset_image = OffsetImage(soleil.image, zoom=zoom_soleil)

    # Liste pour stocker les objets AnnotationBbox
    annotations = []

    def init():
        for scatter in scatters.values():
            scatter.set_data([], [])
        return scatters.values()

    def update(frame):
        for corps in corps_celestes:
            corps.maj_force(corps_celestes)
            corps.maj_position_et_vitesse(dt)
            positions[corps.nom].append(corps.position.copy())

        for annotation in annotations:
            annotation.remove()
        annotations.clear()

        for corps in corps_celestes:
            if corps.nom != "Soleil":
                ab = AnnotationBbox(corps.offset_image, corps.position, frameon=False)
                ax.add_artist(ab)
                annotations.append(ab)

        ab_soleil = AnnotationBbox(soleil.offset_image, soleil.position, frameon=False)
        ax.add_artist(ab_soleil)
        return annotations + [ab_soleil]

    ani = FuncAnimation(fig, update, frames=total_steps, init_func=init, blit=True, repeat=False)

    plt.show()
    afficher_tableau(corps_celestes)

# Créer la fenêtre principale
root = Tk()
root.withdraw()  # Cacher la fenêtre principale

# Lancer la simulation
run_simulation()

# Fermer l'application après la simulation
root.destroy()