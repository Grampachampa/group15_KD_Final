from rdflib import Graph
import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(current_dir)
final_onto = os.path.join(current_dir, 'final_output.ttl')

def load_graph(graph, filename):
    with open(filename, 'r') as f:
        graph.parse(f, format='turtle')

g = Graph()
load_graph(g, final_onto)

df = pd.read_csv(os.path.join(root, 'weather_data/nl_weather_data.csv'), low_memory=False)
dates = df['YYYYMMDD'].iloc[:365].values


for date in dates:

    
    data_query = """
    PREFIX geo:  <http://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>

    SELECT DISTINCT ?station ?station_name ?station_code ?ts_lat ?ts_long ?delay ?ws ?ws_name ?ws_code ?ws_lat ?ws_long ?windspeed ?mean_temp ?percipitation ?visibility ?wind_direction
        WHERE {
        ?traindata tr:on_date tr:""" + str(date) + """ ;
            tr:hasAverageDelay ?delay ;
            tr:parent_station ?station .

        ?station tr:has_closest_weatherstation ?ws;
            geo:lat ?ts_lat ;
            geo:long ?ts_long ;
            foaf:name ?station_name ;
            dbp:code ?station_code .

        ?weatherdata tr:on_ws ?ws ;
            tr:on_date tr:""" + str(date) + """ ;
            tr:has_max_windspeed ?windspeed ;
            tr:has_mean_temp ?mean_temp ;
            tr:has_percipitation ?percipitation ;
            tr:has_visibility ?visibility ;
            tr:has_wind_direction ?wind_direction .
        
            ?ws foaf:name ?ws_name ;
                dbp:code ?ws_code ;
                geo:lat ?ws_lat ;
                geo:long ?ws_long .


        }
    
""" 
    data = Graph.query(g, data_query)
    df = pd.DataFrame(data, columns=data.vars)
    df.to_csv(os.path.join(current_dir, os.path.join('daily_data',f'{date}.csv')))
    print(f'{date} done')