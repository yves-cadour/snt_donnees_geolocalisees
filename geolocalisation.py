import os
import csv
import requests
import folium
from folium import FeatureGroup, LayerControl, Map, Marker, Popup, IFrame
from folium.plugins import MiniMap, MarkerCluster
from jinja2 import Environment, FileSystemLoader

local_file = "geolocalisation.csv"


def telecharger_donnes():
    """
    Télécharge le fichier si nécessaire
    """
    URL = "https://www.data.gouv.fr/fr/datasets/r/d7f3ddf4-2225-4ac2-9a1d-26971ce92969"
    if not local_file in os.listdir():
        data = requests.get(URL).content
        with open(local_file, 'wb') as csvfile:
            csvfile.write(data)

def creer_carte():
    """
    Creer et retourne une carte Folium
    """
    carte = Map(location=[0,0], width="%100", height="%100", zoom_start=10)
    minimap = MiniMap()
    carte.add_child(minimap)
    # Creation des calques et des clusters
    #  Carte
    #   |
    #   +--+ Calque des 'gratuits'
    #   |  |
    #   |  +-- Cluster des 'gratuits'
    #   |
    #   +--+ Calque des 'payants'
    #   |  |
    #   |  +-- Cluster des 'payants'
    #   |
    #   +--+ Calque des 'Tarifs non communiqués'
    #   |  |
    #   |  +-- Cluster des 'Tarifs non communiqués'
    #   |
    #   +--+ Calque des 'Libre participation'
    #      |
    #      +-- Cluster des 'Libre participation'

    gratuit_layer = folium.FeatureGroup(name="Gratuit")
    gratuit_cluster = MarkerCluster().add_to(gratuit_layer)
    carte.add_child(gratuit_layer)

    payant_layer = folium.FeatureGroup(name="Payant")
    payant_cluster = MarkerCluster().add_to(payant_layer)
    carte.add_child(payant_layer)

    unknown_layer = folium.FeatureGroup(name="Tarifs non communiqués")
    unknown_cluster = MarkerCluster().add_to(unknown_layer)        
    carte.add_child(unknown_layer)

    libre_participation_layer = folium.FeatureGroup(name="Libre participation")
    libre_participation_cluster = MarkerCluster().add_to(libre_participation_layer)        
    carte.add_child(libre_participation_layer)
    
    carte.add_child(folium.map.LayerControl())
    somme_latitude = 0
    somme_longitude = 0
    compteur = 0
    with open(local_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        lignes = list(reader)
        for ligne in lignes:
            code_postal = ligne['detailidentadressecp']
            code_postal = int(''.join(code_postal.split(' ')))
            if code_postal in range(29000,29200):  # Modifiez l'intervalle si vous voulez plus ou moins de résultats.
                latitude = ligne['gmaplatitude']
                longitude = ligne['gmaplongitude']
                tooltip = ligne['syndicobjectname']
                # Rendu du popup
                html = render_html(ligne)
                iframe = IFrame(html)
                popup = Popup(iframe, min_width=800, max_width=800)
                # Rendu de l'icône du marker
                icon = get_icon(ligne)

                # Creation du marker
                marker = Marker([latitude, longitude], icon=icon, popup=popup, tooltip=tooltip)
                compteur += 1
                somme_latitude += float(latitude)
                somme_longitude += float(longitude)
                # On enregistre le marker dans le bon cluster
                if ligne['tarifentree'] == 'Gratuit':
                    marker.add_to(gratuit_cluster)
                elif ligne['tarifentree'] == 'Payant':
                    marker.add_to(payant_cluster)
                elif ligne['tarifentree'] == 'Tarifs non communiqués':
                    marker.add_to(unknown_cluster)
                else:
                    marker.add_to(libre_participation_layer)
        latitude_moyenne = somme_latitude/compteur
        longitude_moyenne = somme_longitude/compteur
        # On centre la carte sur la position moyenne
        carte.location = (latitude_moyenne, longitude_moyenne)
    return carte

def main():
    """
    Affiche la carte des données
    Sauvegarde la carte dans le fichier index.html
    """
    telecharger_donnes()
    carte = creer_carte()
    return carte
    
def get_icon(ligne):
    """
    Retourne l'icone adequat
    ligne : un dictionnaire représentant une ligne des données
    """
    icone = folium.Icon(color = 'red', icon = 'cloud', prefix = 'fa')
    return icone
        
def render_html(ligne):
    """
    Retourne le code html
    """
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('popup.html')
    output = template.render(ligne = ligne)
    return output
    
carte = main()
carte.save("carte.html")
print("Ouvrir le fichier 'carte.html' avec un navigateur web.")
    
            



