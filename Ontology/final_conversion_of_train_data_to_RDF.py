import csv, json, os
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, RDFS, XSD, OWL, FOAF

input_csv_file = '/Users/bedirhangursoy/group15_KD_Final/train_data/clean_train_data.csv'


with open(input_csv_file, mode='r') as file:
    print('opening and reading file...')
    reader = csv.reader(file)
    data = list(reader)


# Create a dictionary to store the data
data_dict = {}
print('creating dictionary')
for line in data[1:]:
    print(line)
    parts = line
    date = parts[0]
    station_name = parts[4]
    arrival_delay = parts[5]
    station_code = parts[3]

    # Initialize the dictionary for the date
    if date not in data_dict:
        data_dict[date] = []

    # Check if the station is already in the list for the date
    station_exists = False
    for entry in data_dict[date]:
        if entry[0] == station_name:
            if arrival_delay:
                entry[1].append(float(arrival_delay))
            station_exists = True
            break

    # If the station is not in the list, add it
    if not station_exists and arrival_delay:
        data_dict[date].append([station_name, [float(arrival_delay)], station_code])

# Calculate the average delay for each station on each date
for date in data_dict:
    for entry in data_dict[date]:
        avg_delay = sum(entry[1]) / len(entry[1])
        entry[1] = avg_delay
def load_graph(graph_name, filename):
    with open(filename, 'r') as f:
        graph_name.parse(f, format='turtle')

g = Graph()
current_dir = os. getcwd()
print('opening graph')
train_ontology = os.path.join(current_dir, 'tr - Copy.ttl')
load_graph(g, train_ontology)
tr = Namespace("http://www.group15_KD_tr_onto/")
g.bind("tr", tr)

dbp = Namespace('http://dbpedia.org/property/')
g.bind('dbp', dbp)


print('creating RDF file')

for date, station_data in data_dict.items():
    date_uri = URIRef(tr[date])
    for station_name, avg_delay, station_code in station_data:
        print(date, station_data, station_name, avg_delay, station_code)
        subject = f'{station_code}_{date}'
        station_uri = URIRef(tr[subject])
        station_code_URI = URIRef(tr[station_code])
        g.add((station_uri, RDF.type, tr[f"Station_Data_{station_code}"]))
        g.add((station_code_URI, RDF.type, tr['Train_Station']))
        g.add((station_uri, tr["on_date"], date_uri))
        g.add((date_uri, tr["was_date_for"], station_uri))
        g.add((station_uri, FOAF.name, Literal(station_name)))
        g.add((station_uri, tr["hasAverageDelay"], Literal(avg_delay, datatype=XSD.float)))
        g.add((station_uri, dbp["code"], Literal(station_code)))
        g.add((station_uri, tr['parent_station'], tr[station_code]))
        g.add((tr[f"Station_Data_{station_code}"], RDFS.subClassOf, tr['Station_Data']))

# Serialize the graph to a Turtle file
output_file = "final_output.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"Data has been saved to {output_file}")
