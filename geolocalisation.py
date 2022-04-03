import os
import csv
import requests
import folium
from folium import FeatureGroup, LayerControl, Map, Marker, Popup, IFrame
from folium.plugins import MiniMap, MarkerCluster
from jinja2 import Environment, FileSystemLoader

URL = "https://www.data.gouv.fr/fr/datasets/r/d7f3ddf4-2225-4ac2-9a1d-26971ce92969"


def display_map(url):
    """Affiche la carte des données qui se trouvent à 'url'
    """
    local_file = "geolocalisation.csv"
    if not local_file in os.listdir():
        data = requests.get(url).content
        with open(local_file, 'wb') as csvfile:
            csvfile.write(data)
    with open(local_file) as csvfile:
        m = Map(location=[0,0], width="%100", height="%100", zoom_start=10)
        #marker_cluster = MarkerCluster().add_to(m)
        minimap = MiniMap()
        m.add_child(minimap)
        # Creation des clusters et des couches
        gratuit_layer = folium.FeatureGroup(name="Gratuit")
        gratuit_cluster = MarkerCluster().add_to(gratuit_layer)
        m.add_child(gratuit_layer)

        payant_layer = folium.FeatureGroup(name="Payant")
        payant_cluster = MarkerCluster().add_to(payant_layer)
        m.add_child(payant_layer)

        unknown_layer = folium.FeatureGroup(name="Tarifs non communiqués")
        unknown_cluster = MarkerCluster().add_to(unknown_layer)        
        m.add_child(unknown_layer)

        libre_participation_layer = folium.FeatureGroup(name="Libre participation")
        libre_participation_cluster = MarkerCluster().add_to(libre_participation_layer)        
        m.add_child(libre_participation_layer)
        m.add_child(folium.map.LayerControl())

        
        reader = csv.DictReader(csvfile, delimiter=';')
        somme_latitude = 0
        somme_longitude = 0
        compteur = 0
        for row in reader:
            code_postal = row['detailidentadressecp']
            code_postal = int(''.join(code_postal.split(' ')))
            if code_postal in range(29000,30000):# and row['multimediaphoto']:
                #if row['multimediaphoto']:
                #    for key in row.keys():
                #        print(key+":"+row[key])
                #    print('----')
                compteur += 1
                latitude = row['gmaplatitude']
                longitude = row['gmaplongitude']
                somme_latitude += float(latitude)
                somme_longitude += float(longitude)
                tooltip = row['syndicobjectname']
                html = render_html(row)
                iframe = IFrame(html)
                popup = Popup(iframe, min_width=800, max_width=800)
                icon = get_icon(row)
                marker = Marker([latitude, longitude], icon=icon, popup=popup, tooltip=tooltip)
                if row['tarifentree'] == 'Gratuit':
                    marker.add_to(gratuit_cluster)
                elif row['tarifentree'] == 'Payant':
                    marker.add_to(payant_cluster)
                elif row['tarifentree'] == 'Tarifs non communiqués':
                    marker.add_to(unknown_cluster)
                else:
                    marker.add_to(libre_participation_layer)

                
        moy_latitude = somme_latitude/compteur
        moy_longitude = somme_longitude/compteur
        m.location = (moy_latitude, moy_longitude)
        return m
    
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
    
m = display_map(URL)
m.save("index.html")
    
            



