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

station_codes = os.path.join(current_dir, 'station_codes.csv')

lines = []
with open(station_codes, 'r') as stations:
    read_stations = csv.reader(stations)
    for row in read_stations:

        line = ''.join([x for x in row[0] if not x.isdigit()]).strip().split(" ")
        line = [' '.join(map(str,line[:-1])), line[-1]]
        lines.append(line)

# print (lines[12])
with open(station_codes, 'w') as stations:
    wstations = csv.writer(stations, lineterminator="\n")
    for line in lines:
        wstations.writerow(line)
