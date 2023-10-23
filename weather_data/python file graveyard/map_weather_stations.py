import os
import csv
import folium
import math
from PIL import Image
import io
from SPARQLWrapper import SPARQLWrapper, JSON


# Get the full path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

weather_data = os.path.join(current_dir, 'nl_weatherstation_locations.csv')

coordinates = {}

with open(weather_data, 'r') as weather:
    weatherdict = csv.DictReader(weather)
    for row in weatherdict:
        coordinates[row["STN"]] = [float(row["LATTITUDE"]), float(row["LONGITUDE"])]


lats = [j[0] for i, j in coordinates.items()]
longs = [j[1] for i, j in coordinates.items()]

middle = [sum(lats)/len(lats), sum(longs)/len(longs)]
m = folium.Map(location=middle, zoom_start=8)

mindistance = {}

for id, coordinate in coordinates.items():
    min_distance = float("inf")
    for id2, coordinate2 in coordinates.items():
        if id == id2:
            continue
        
        R = 6373.0

        lat1 = math.radians(coordinate[0])
        lon1 = math.radians(coordinate[1])
        lat2 = math.radians(coordinate2[0])
        lon2 = math.radians(coordinate2[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        if distance < min_distance:
            min_distance = distance
            mindistance[id] = distance

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery(f"""
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX georss: <http://www.georss.org/georss/>
PREFIX yago: <http://dbpedia.org/class/yago/>
PREFIX geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
PREFIX wikidata: <http://www.wikidata.org/entity/>
PREFIX dbp: <http://dbpedia.org/property/>

SELECT DISTINCT ?location ?name ?lat ?long
WHERE {{
    {{
        ?location a wikidata:Q719456;
                  dbp:style ?style;
                  rdfs:label ?name;
                  geo:lat ?lat;
                  geo:long ?long.
        FILTER (
            contains(?style, "NS") &&
            langMatches(lang(?style),'en') &&
            langMatches(lang(?name),'en') &&
            ?lat > 50.709572 && ?lat < 54.092432 &&
            ?long > 2.950305 && ?long < 7.547854  
        )
    }} UNION {{
        BIND(<http://dbpedia.org/resource/Amsterdam_Centraal_station> AS ?location)
        ?location dbp:style ?style;
                rdfs:label ?name;
                geo:lat ?lat;
                geo:long ?long.
        FILTER (
            langMatches(lang(?style),'en') &&
            langMatches(lang(?name),'en') &&
            ?lat > 50.709572 && ?lat < 54.092432 &&
            ?long > 2.950305 && ?long < 7.547854  
        )
    }}
}}
    LIMIT 401
""")
stationcoords = {}
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    stationcoords[result["name"]["value"]] = [float(result["lat"]["value"]), float(result["long"]["value"])]


for name, place_coordinates in coordinates.items():
    if place_coordinates == "":
        continue
    folium.Circle(
        location = place_coordinates,
        radius= 100, 
        popup= name,
        color="#3186cc",
        fill=False,
        fill_color="#3186cc",
        
    ).add_to(m)


station_ids = {}
trainstation_id_file = os.path.join(os.path.join(os.path.dirname(current_dir), "train_data"), 'station_codes.csv')
with open(trainstation_id_file, 'r') as ids:
    iddict = csv.DictReader(ids)
    for row in iddict:
        station_ids[row["STATION"]] = row["CODE"].upper()

station_ids_copy = station_ids.copy()
for coordstation in stationcoords:
    for idstation in station_ids_copy:
        if idstation.lower() in coordstation.lower() or coordstation.lower() in idstation.lower():
            station_ids[coordstation] = station_ids[idstation]
errors = []
for name, place_coordinates in stationcoords.items():
    if place_coordinates == "":
        continue
    try:
        folium.Circle(
            location = place_coordinates,
            radius= 100, 
            popup= station_ids[name],
            color="#FF0000",
            fill=False,
            fill_color="#FF0000",
            
        ).add_to(m)
    except:
        errors.append(name)
        continue
print("errors", errors, sep="\n")
folium.TileLayer('cartodbdark_matter').add_to(m)
m.save("map.html")

print(len(stationcoords))

#img_data = m._to_png(5)
#img = Image.open(io.BytesIO(img_data))
#img.save('image.png')