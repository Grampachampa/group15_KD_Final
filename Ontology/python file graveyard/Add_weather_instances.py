from rdflib import Graph, RDF, Namespace, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper
import pandas as pd

owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
train = Namespace('http://www.semanticweb.org/gramp/ontologies/2023/9/untitled-ontology-23/')
foaf = Namespace('http://xmlns.com/foaf/0.1/')


def load_graph(graph, filename):
    with open(filename, 'r') as f:
        graph.parse(f, format='turtle')
        

def serialize_graph(myGraph):
     print(myGraph.serialize(format='turtle'))
        

def save_graph(myGraph, filename):
    with open(filename, 'w') as f:
        myGraph.serialize(filename, format='turtle')





g = Graph()
load_graph(g, 'Ontology/example_ontology.ttl')


df = pd.read_csv('weather_data/nl_weather_data.csv', low_memory=False)

df = df[['YYYYMMDD', 'STN', 'NAME']]

for index, row in df.iterrows():

    #add weatherstations and dates to ontology

    g.add((URIRef(train[str(row['STN'])]), RDF.type, train['Weatherstation'])) 
    g.add((URIRef(train[str(row['YYYYMMDD'])]), RDF.type, train['Date']))
    g.add((URIRef(train[str(row['STN'])]), foaf['has_name'], train[str(row['NAME'].replace(" ", "_"))]))
    

serialize_graph(g)
save_graph(g, 'Ontology/train_ontology.ttl')


   


