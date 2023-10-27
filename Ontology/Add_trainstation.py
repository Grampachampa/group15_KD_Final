import os
import csv
from rdflib import Graph, RDF, Namespace, Literal, URIRef
import math
from SPARQLWrapper import SPARQLWrapper, JSON


# Step 1: Get the path to the current file. This will be useful later.
current_dir = os.path.dirname(os.path.abspath(__file__))


# Step 2: Query dbpedia for all trainstations in the netherlands. 
# (Ams Centraal is defined differently, and has to be queried for separately)
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

# we then store the coordinates of the trainstations in a dictionary
# key: name; value: coords
dbpedia_ts_coords: dict[str:list[float]] = {}
dbpedia_ts_sameAs: dict[str:str] = {}
sparql.setReturnFormat(JSON)
results = sparql.query().convert()
for result in results["results"]["bindings"]:
    dbpedia_ts_coords[result["name"]["value"]] = [float(result["lat"]["value"]), float(result["long"]["value"])]
    dbpedia_ts_sameAs[result["name"]["value"]] = result["location"]["value"]


# Step 3: read the file listing the trainstation ids; store station ids
ts_station_ids = {}
trainstation_id_file = os.path.join(os.path.join(os.path.dirname(current_dir), "train_data"), 'station_codes.csv')
with open(trainstation_id_file, 'r') as ids:
    iddict = csv.DictReader(ids)
    for row in iddict:
        ts_station_ids[row["STATION"]] = row["CODE"].upper()

ts_station_ids_copy = ts_station_ids.copy()

for coordstation in dbpedia_ts_coords:
    for idstation in ts_station_ids_copy:
        if idstation.lower() in coordstation.lower() or coordstation.lower() in idstation.lower():
            ts_station_ids[coordstation] = ts_station_ids[idstation]

 



counter = 0

id_coord_dict: dict[str: tuple[str, list[float]]] = {}
ts_sameAs = {}

for station, coords in dbpedia_ts_coords.items():
    try:
        id_coord_dict[ts_station_ids[station]] = (station, coords)
        ts_sameAs[ts_station_ids[station]] = dbpedia_ts_sameAs[station]
        counter += 1
    except:
        pass

print(counter)






stn_to_name: dict[str:str] = {}
weather_data = os.path.join(os.path.join(os.path.dirname(current_dir), "weather_data"), 'nl_weatherstation_locations.csv')
with open(weather_data, 'r') as weather:
    weatherdict = csv.DictReader(weather)
    coordinates = {}
    for row in weatherdict:
        coordinates[row["STN"]] = [float(row["LATTITUDE"]), float(row["LONGITUDE"])]
        stn_to_name[row["STN"]] = row["NAME"]



# at this point, we have everything we need to start adding things

owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
train = Namespace('http://www.group15_KD_tr_onto/')
foaf = Namespace('http://xmlns.com/foaf/0.1/')
geo = Namespace('http://www.w3.org/2003/01/geo/wgs84_pos#')
dbp = Namespace('http://dbpedia.org/property/')
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")



def load_graph(graph, filename):
    with open(filename, 'r') as f:
        graph.parse(f, format='turtle')
        

def serialize_graph(myGraph):
     print(myGraph.serialize(format='turtle'))
        

def save_graph(myGraph, filename):
    with open(filename, 'w') as f:
        myGraph.serialize(filename, format='turtle')

g = Graph()


# NOTE: the following are the dicts: 
# mindistance[ts_id:ws_id]; 
# coordinates[ws_id:[ws_lat,ws_long]]; 
# id_coord_dict[ts_id: (ts_name, [ts_lat, ts_long])]

train_ontology = os.path.join(current_dir, "tr - Copy.ttl")
load_graph(g, train_ontology)
for ts_id, ts_contents in id_coord_dict.items():
    ts_name, ts_coords = ts_contents
    ts_lat, ts_long = ts_coords

    # create train station
    g.add((URIRef(train[str(ts_id)]), RDF.type, train['Train_Station']))

    # add coords
    g.add((URIRef(train[str(ts_id)]), geo.lat, Literal(ts_lat, datatype=xsd.float))) 
    g.add((URIRef(train[str(ts_id)]), geo.long, Literal(ts_long, datatype=xsd.float))) 
    g.add((URIRef(train[str(ts_id)]), owl.sameAs, URIRef(ts_sameAs[ts_id]))) 
    g.add((URIRef(ts_sameAs[ts_id]), RDF.type, train['Train_Station']))


    # add closest weatherstation
    #g.add((URIRef(train[str(ts_id)]), train['has_closest_weatherstation'], URIRef(train[str(mindistance[ts_id])])))
    

    # add name
    g.add((URIRef(train[str(ts_id)]), foaf.name, Literal(ts_name)))
    # add code
    g.add((URIRef(train[str(ts_id)]), dbp.code, Literal(ts_id)))
    

for ws_id, ws_coords in coordinates.items():
    ws_lat, ws_long = ws_coords

    # add coords
    g.add((URIRef(train[str(ws_id)]), RDF.type, train['Weatherstation']))
    g.add((URIRef(train[str(ws_id)]), foaf.name, Literal(stn_to_name[ws_id]))) 
    g.add((URIRef(train[str(ws_id)]), dbp.code, Literal(ws_id)))
    g.add((URIRef(train[str(ws_id)]), geo.lat, Literal(ws_lat, datatype=xsd.float))) 
    g.add((URIRef(train[str(ws_id)]), geo.long, Literal(ws_long, datatype=xsd.float)))
    g.add((URIRef(train[str(ws_id)]), dbp.code, Literal(ws_id)))



# Fun time: now we get all the weather and connect it to the date!!!

weather_by_date = os.path.join(os.path.join(os.path.dirname(current_dir), "weather_data"), 'nl_weather_data.csv')
useless_set = set()
weather_phenomena_usefullness_list = []
with open(weather_by_date) as weather_dates:
    daily_w_dict = csv.DictReader(weather_dates)

    for row in daily_w_dict:
        wind_direction = row["DDVEC"] if row["DDVEC"] != "  " else None
        max_windspeed = row["FHX"] if row["FHX"] != "  " else None
        mean_temp = row["TG"] if row["TG"] != "  " else None
        percipitation = row["RH"] if row["RH"] != "  " else None
        visibility = row["VVN"] if row["VVN"] != "  " else None
        ws_id = row["STN"].upper()
        date = row["YYYYMMDD"]

        individ_name = str(ws_id + "_" + date)

        g.add((URIRef(train[individ_name]), RDF.type, train[f"Weather_Phenomenon"]))
        g.add((URIRef(train[individ_name]), train["on_ws"], URIRef(train[str(ws_id)])))

        
        if wind_direction is not None:
            g.add((URIRef(train[individ_name]), train.has_wind_direction, Literal(int(wind_direction), datatype=xsd.integer))) 
        
        if max_windspeed is not None:
            g.add((URIRef(train[individ_name]), train.has_max_windspeed, Literal(int(max_windspeed), datatype=xsd.integer)))
        if mean_temp is not None:
            g.add((URIRef(train[individ_name]), train.has_mean_temp, Literal(int(mean_temp), datatype=xsd.integer)))
        if percipitation is not None:
            g.add((URIRef(train[individ_name]), train.has_percipitation, Literal(int(percipitation), datatype=xsd.integer)))
        if visibility is not None:
            g.add((URIRef(train[individ_name]), train.has_visibility, Literal(int(visibility), datatype=xsd.integer)))

        if None in [wind_direction, max_windspeed, mean_temp, percipitation, visibility]:
            # g.add((URIRef(train[individ_name]), train.is_useless, Literal(True, datatype=xsd.boolean)))
            # g.add((URIRef(train[individ_name]), RDF.type, train[f"Not_Useful_Weather_Phenomenon"]))
            useless_set.add(ws_id)
        # else:
        #     g.add((URIRef(train[individ_name]), train.is_useless, Literal(False, datatype=xsd.boolean)))
        #     g.add((URIRef(train[individ_name]), RDF.type, train[f"Useful_Weather_Phenomenon"]))
        g.add((URIRef(train[individ_name]), train.on_date, train[date]))
        weather_phenomena_usefullness_list.append((ws_id, individ_name))

for id, instance_name in weather_phenomena_usefullness_list:
    if id in useless_set:
        g.add((URIRef(train[instance_name]), train.is_useless, Literal(True, datatype=xsd.boolean)))
        g.add((URIRef(train[instance_name]), RDF.type, train[f"Not_Useful_Weather_Phenomenon"]))
    else:
        g.add((URIRef(train[instance_name]), train.is_useless, Literal(False, datatype=xsd.boolean)))
        g.add((URIRef(train[instance_name]), RDF.type, train[f"Useful_Weather_Phenomenon"]))



mindistance = {}
for ts_id, ts_contents in id_coord_dict.items():
    ts_name, ts_coords = ts_contents
    ts_latitude, ts_longitude = ts_coords
    min_distance = float("inf")
    for ws_id, ws_coords in coordinates.items():
        if ws_id in useless_set:
            continue
        ws_latitude, ws_longitude = ws_coords
  
        R = 6373.0

        lat1 = math.radians(ts_latitude)
        lon1 = math.radians(ts_longitude)
        lat2 = math.radians(ws_latitude)
        lon2 = math.radians(ws_longitude)

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        if distance < min_distance:
            min_distance = distance
            mindistance[ts_id] = ws_id
    print(ts_id, mindistance[ts_id], sep=" | ")

for ts_id, ts_contents in id_coord_dict.items():
    ts_name, ts_coords = ts_contents
    ts_lat, ts_long = ts_coords

    # add closest weatherstation
    g.add((URIRef(train[str(ts_id)]), train['has_closest_weatherstation'], URIRef(train[str(mindistance[ts_id])])))
    

save_graph(g, train_ontology)
print (len(coordinates) - len(useless_set), len(coordinates), sep="/")