import pandas as pd
import matplotlib.pyplot as plt

def afficher_tableau(corps_celestes):
    data = []
    for corps in corps_celestes:
        distance = (corps.position[0]**2 + corps.position[1]**2)**0.5
        data.append({
            "Nom": corps.nom,
            "Masse (kg)": f"{corps.masse:.3e}",
            "Position (km)": f"({corps.position[0]:.2e}, {corps.position[1]:.2e})",
            "Vitesse (km/s)": f"({corps.vitesse[0]:.2e}, {corps.vitesse[1]:.2e})",
            "Distance au Soleil (km)": f"{distance:.2e}"
        })

    df = pd.DataFrame(data)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    plt.title("Informations des Corps Célestes", fontsize=14)
    plt.show()


    