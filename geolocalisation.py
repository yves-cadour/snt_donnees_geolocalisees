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
        data = requests.get(url).content
        with open(local_file, 'wb') as csvfile:
            csvfile.write(data)

def jls_extract_def(somme_latitude, lignes, somme_longitude):
    moy_latitude = somme_latitude/len(lignes)
    moy_longitude = somme_longitude/len(lignes)
    return moy_latitude, moy_longitude


def creer_carte():
    """
    Creer et retourne une carte Folium
    """
    carte = Map(location=[0,0], width="%100", height="%100", zoom_start=8)
    minimap = MiniMap()
    carte.add_child(minimap)
    # Creation des clusters et des couches
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
    with open(local_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        lignes = list(reader)
        for ligne in lignes:
            #print(ligne)
            code_postal = ligne['detailidentadressecp']
            code_postal = int(''.join(code_postal.split(' ')))
            if code_postal in range(29000,29200):
                latitude = ligne['gmaplatitude']
                longitude = ligne['gmaplongitude']
                somme_latitude += float(latitude)
                somme_longitude += float(longitude)
                tooltip = ligne['syndicobjectname']
                html = render_html(ligne)
                iframe = IFrame(html)
                popup = Popup(iframe, min_width=800, max_width=800)
                icon = get_icon(ligne)
                marker = Marker([latitude, longitude], icon=icon, popup=popup, tooltip=tooltip)
                if ligne['tarifentree'] == 'Gratuit':
                    marker.add_to(gratuit_cluster)
                elif ligne['tarifentree'] == 'Payant':
                    marker.add_to(payant_cluster)
                elif ligne['tarifentree'] == 'Tarifs non communiqués':
                    marker.add_to(unknown_cluster)
                else:
                    marker.add_to(libre_participation_layer)

        carte.location = (lignes[0]['gmaplatitude'], lignes[0]['gmaplongitude'])
    return carte

def main():
    """
    Affiche la carte des données
    Sauvegarde la carte dans le fichier index.html
    """
    telecharger_donnes()
    carte = creer_carte()
    return carte
    
def get_icon(row):
    """
    Retourne l'icone adequat
    """
    if row['tarifentree'] == 'Gratuit':
        icon=folium.Icon(color='red', icon='home', prefix='fa')
    elif row['tarifentree'] == 'Payant':
        icon=folium.Icon(color='green', icon='home', prefix='fa')
    elif row['tarifentree'] == 'Tarifs non communiqués':
        icon=folium.Icon(color='blue', icon='home', prefix='fa')
    else:
        icon=folium.Icon(color='black', icon='home', prefix='fa')
    return icon
        
def render_html(row):
    """
    Retourne le code html
    """
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)
    template = env.get_template('display_row.html')
    output = template.render(row=row)
    return output
    
carte = main()
carte.save("index.html")
    
            



