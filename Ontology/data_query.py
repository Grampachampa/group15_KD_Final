from rdflib import Graph, RDF, Namespace, Literal, URIRef
from SPARQLWrapper import SPARQLWrapper
import pandas as pd
from IPython.display import display


def load_graph(graph, filename):
    with open(filename, 'r') as f:
        graph.parse(f, format='turtle')

g = Graph()
load_graph(g, 'Ontology/final_output.ttl')

df = pd.read_csv('weather_data/nl_weather_data.csv', low_memory=False)
dates = df['YYYYMMDD'].iloc[:365].values


for date in dates[:1]:

    
    data_query = """

    SELECT DISTINCT ?station ?delay ?ws ?windspeed ?mean_temp ?percipitation ?visibility ?wind_direction
        WHERE {
        ?traindata tr:on_date tr:""" + str(date) + """ ;
        tr:hasAverageDelay ?delay ;
        tr:parent_station ?station .
        ?station tr:has_closest_weatherstation ?ws .
        ?weatherdata tr:on_ws ?ws ;
        tr:on_date tr:""" + str(date) + """ ;
        tr:has_max_windspeed ?windspeed ;
        tr:has_mean_temp ?mean_temp ;
        tr:has_percipitation ?percipitation ;
        tr:has_visibility ?visibility ;
        tr:has_wind_direction ?wind_direction .
        
        }
    
""" 
    data = Graph.query(g, data_query)
    df = pd.DataFrame(data, columns=data.vars)
    print(df)
    




