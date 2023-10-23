import os
import csv
import folium
import math
from PIL import Image
import io
from rdflib import Graph, RDF, RDFS, Namespace, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON

# Get the full path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

data_file = os.path.join(current_dir, 'nl_weather_data.csv')

coordinates = {}

with open(data_file, 'r') as csvfile:
    dictreader = csv.DictReader(csvfile)
    for row in dictreader:
        coordinates[row["NAME"]] = ''

empty_coords = []

for name in coordinates:
    print ("Searching for: " + name)
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(f"""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX georss: <http://www.georss.org/georss/>
    PREFIX yago: <http://dbpedia.org/class/yago/>
    PREFIX geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#>

    SELECT ?location ?name ?lat ?long
    WHERE {{
        ?location a yago:YagoGeoEntity;
                rdfs:label ?name;
                geo:lat ?lat;
                geo:long ?long.
        FILTER (
            contains(?name, "{name}") &&
            langMatches(lang(?name),'en') &&
            ?lat > 50.709572 && ?lat < 54.092432 &&
            ?long > 2.950305 && ?long < 7.547854
        )
    }}
    LIMIT 1
""")
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        print(f'Name: {result["name"]["value"]}\nLink: {result["location"]["value"]}\nCoords: {result["lat"]["value"]}, {result["long"]["value"]}\n')
        coordinates[name] = [float(result["lat"]["value"]), float(result["long"]["value"])]
        break
    else:
        print(f"{name} not found\n")
        empty_coords.append(name)

not_found = len(empty_coords)
found = len(coordinates)
print(f"DONE! {found-not_found}/{found} coordinates found. Not found:")
for i in empty_coords:
    print(i)

lats = [j[0] for i, j in coordinates.items() if j != '']
longs = [j[1] for i, j in coordinates.items() if j != '']

middle = [sum(lats)/len(lats), sum(longs)/len(longs)]

m = folium.Map(location=middle, zoom_start=8)


for name, place_coordinates in coordinates.items():
    if place_coordinates == "":
        continue
    folium.CircleMarker(
        location = place_coordinates,
        radius= 1, 
        popup= name,
        color="#3186cc",
        fill=False,
        fill_color="#3186cc",
        
    ).add_to(m)
    
folium.TileLayer('cartodbdark_matter').add_to(m)
m.save("map.html")


img_data = m._to_png(5)
img = Image.open(io.BytesIO(img_data))
img.save('image.png')