import csv, json
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef, RDFS, XSD, OWL

input_csv_file = 'temp_train_data.csv'

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

g = Graph()
print('create that graph')
# Define namespaces
tr = Namespace("http://example.org/")
g.bind("tr", tr)

print('creating RDF file')
for date, station_data in data_dict.items():
    date_uri = URIRef(tr[date])
    for station_name, avg_delay, station_code in station_data:
        print(date, station_data, station_name, avg_delay, station_code)
        subject = f'{station_code}_{date}'
        station_uri = URIRef(tr[subject])
        station_code_URI = URIRef(tr[station_code])
        g.add((station_uri, RDF.type, tr[f"StationData_{station_code}"]))
        g.add((station_code_URI, RDF.type, tr['StationCode']))
        g.add((station_uri, tr["hasDate"], Literal(date_uri)))
        g.add((station_uri, tr["hasName"], Literal(station_name)))
        g.add((station_uri, tr["hasAverageDelay"], Literal(avg_delay, datatype=XSD.float)))
        g.add((station_uri, tr["hasCode"], station_code_URI))

# Serialize the graph to a Turtle file
output_file = "output2.ttl"
g.serialize(destination=output_file, format="turtle")

print(f"Data has been saved to {output_file}")