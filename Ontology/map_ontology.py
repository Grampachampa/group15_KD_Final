import os
import csv
import folium
import math
import branca
import time
from selenium import webdriver
from folium.plugins import HeatMap


def draw_map():

    

    # Get the full path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))

    daily_data = os.path.join(current_dir, 'daily_data')
    file_list : list[tuple[list]] = [x for x in os.walk(daily_data)][0][2:][0]
    

    for file_name in file_list[126:]:
        
        date = file_name.split(".")[0]
        middle = [52.15537999999999, 5.034119999999999]
        m = folium.Map(location=middle, zoom_start=8)

        with open(os.path.join(daily_data, file_name), 'r') as day:
            dictReader = csv.DictReader(day)
            previous = None
            store_area_of_influence = 0
            heat_map_data = set()
            
            for row in dictReader:
                ts_iri = row["station"]
                ts_name = row["station_name"]
                ts_code = row["station_code"]
                ts_lat = row["ts_lat"]
                ts_long = row["ts_long"]
                avg_delay = row["delay"]
                ws_iri = row["ws"]
                ws_name = row["ws_name"]
                ws_code = row["ws_code"]
                ws_lat = row["ws_lat"]
                ws_long = row["ws_long"]

                # Wind (arrow)
                windspeed = float(row["windspeed"])*0.1
                wind_direction = row["wind_direction"]
                
                # rest (color)
                mean_temp = row["mean_temp"]
                percipitation = row["percipitation"]
                visibility = row["visibility"]

                if previous != [ws_lat, ws_long] and previous != None:
                    
                    add_zone_of_influence(previous, store_area_of_influence*1000, previous_weather, m, heat_map_data)
                    store_area_of_influence = 0
                    previous_weather = [mean_temp, percipitation, visibility]


                distance = find_distance([float(ws_lat), float(ws_long)], [float(ts_lat), float(ts_long)])
                if distance > store_area_of_influence:
                    store_area_of_influence = distance
                
                previous = [ws_lat, ws_long]
                previous_weather = [mean_temp, percipitation, visibility]

                
                


                # add ws to map
                center = [float(ws_lat), float(ws_long)]
                side_length_meters = 500  # for a 500m side length

                # Draw a star around the location with the given color
                plus_coords = calculate_plus_coordinates(center, 0.09)

                folium.Polygon(
                    locations=plus_coords,
                    color="#f49ac2",
                    radius=100,
                    fill=True,
                    tooltip=ws_code,
                    popup=ws_name
                ).add_to(m)

                arrow_coords = draw_arrow(center, float(windspeed), float(wind_direction))

                folium.Polygon(
                    locations=arrow_coords,
                    popup=f"{windspeed}m/s",
                    tooltip=f"Direction:\n{wind_direction}",
                    color="#FF0000",
                    fill=True,
                    fill_color="#FF0000",
                    opacity=0.1,
                    fill_opacity=1

                ).add_to(m)


                # add ts to map
                delay = max(0, min(float(avg_delay), 4))
                if delay == 1:
                    delay = 1.01

                if delay <= 0.8:
                    percentage = delay / 0.8 * 0.5
                else:
                    log_val = math.log(delay + 0.2)
                    percentage = 0.5 + 0.5 * (log_val / math.log(4 +0.2))

                # Base colors
                soft_green = [153, 255, 153]  # RGB values for #99FF99
                red = [255, 0, 0]

                # Calculate the gradient between the two base colors
                color = [
                    int(soft_green[i] + percentage * (red[i] - soft_green[i])) for i in range(3)
                ]

                # Convert to hexadecimal
                ts_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])

                folium.Circle(
                    location=[ts_lat, ts_long],
                    radius=100,
                    popup=ts_name + "\nDelay: " + str(avg_delay),
                    tooltip=ts_code,
                    color=ts_color,
                    fill=False,
                    fill_color=ts_color,
                ).add_to(m)
            
            else:
                add_zone_of_influence(previous, store_area_of_influence*1000, previous_weather, m, heat_map_data)
                

        delay = branca.colormap.LinearColormap(colors=[(153, 255, 153), (255, 0, 0)],
                             index=[0, 4], vmin=0, vmax=4,
                             caption='Average delay of train station [minutes] (color of small circles/dots)')
        svg_style = '<style>svg#legend {background-color: grey;}</style>'
        m.get_root().header.add_child(folium.Element(svg_style))
        delay.add_to(m)
        
        rainfall = branca.colormap.LinearColormap(colors=['#FFFF99', '#ADD8E6', '#00008B'],
                             index=[0, 10, 50], vmin=0, vmax=50,
                             caption='Daily rainfall [mm] (color of large dashed circles)')
        svg_style = '<style>svg#legend {background-color: grey;}</style>'
        m.get_root().header.add_child(folium.Element(svg_style))
        rainfall.add_to(m)

        temp = branca.colormap.LinearColormap(colors=[(255, 255, 255), '#C8C8FF', "#9696FF", "#5C5CFF", (0, 0, 255),'#5134AD', '#855679', '#B2734C',(255, 165, 0)],
                             index=[-10, 0, 5, 8, 10, 12, 15, 20, 40], vmin=-10, vmax=40,
                             caption='Daily mean temperature [°C] (color of aura around weatherstation crosses)')
        svg_style = '<style>svg#legend {background-color: grey;}</style>'
        m.get_root().header.add_child(folium.Element(svg_style))
        temp.add_to(m)

        visibility = branca.colormap.LinearColormap(colors=[(106,90,205,255), (106,90,205, 0)],
                             index=[0,70], vmin=0, vmax=70,
                             caption='Visibility [KM] (Opacity of aura around weatherstation crosses [more opacity = less visibility])')
        svg_style = '<style>svg#legend {background-color: grey;}</style>'
        m.get_root().header.add_child(folium.Element(svg_style))
        visibility.add_to(m)


        template = f"""
{{% macro html(this, kwargs) %}}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NL_WEATHER_TRAIN_Map</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">
</head>

<body>
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:3px solid grey; background-color:rgba(255, 255, 255, 0.7);
    border-radius:6px; padding: 8px; font-size:18px; top: 100px; left: 5%; width: 10%'>

<div class='title-box'>
<div class='main-title'>{date}</div>

<style type='text/css'>
  .title-box .main-title {{
    text-align: center;
    margin-bottom: 0px; 
    font-weight: bold;
    font-size: 150%;
    }}
  .title-box .subtitle {{
    text-align: center;
    margin-bottom: 0px;
    font-weight: normal;
    font-size: 125%;
    }}
</style>
</body>

{{% endmacro %}}"""

        macro = branca.element.MacroElement()
        macro._template = branca.element.Template(template)
        m.get_root().add_child(macro)
                
        folium.TileLayer('cartodbdark_matter').add_to(m)
        m.save(os.path.join(os.path.join(current_dir,"html files"), f'{date}.html'))


        delay=2
        tmpurl=os.path.join(os.path.join(current_dir,"html files"), f'{date}.html')

        browser = webdriver.Firefox(executable_path="C:/Users/gramp/Desktop/Launchers and other stuff/geckodriver-v0.33.0-win64/geckodriver.exe")
        browser.get(tmpurl)
        #Give the map tiles some time to load
        time.sleep(delay)
        browser.save_screenshot(os.path.join(os.path.join(current_dir,"images"), f'{date}.png'))
        browser.quit()
        




# calculate square corners
def calculate_plus_coordinates(center, size):
    thickness = size * 0.016666666666666666
    v_half_size = (size*0.7) / 2
    v_half_thickness = (thickness*1.5) / 2

    h_half_size = size / 2
    h_half_thickness = thickness / 2

    # Vertical line of the plus
    
    v_top_left = [center[0] + v_half_size, center[1] - v_half_thickness]
    v_top_right = [center[0] + v_half_size, center[1] + v_half_thickness]
    v_bottom_left = [center[0] - v_half_size, center[1] - v_half_thickness]
    v_bottom_right = [center[0] - v_half_size, center[1] + v_half_thickness]

    # Horizontal line of the plus
    h_top_left = [center[0] + h_half_thickness, center[1] - h_half_size]
    h_top_right = [center[0] + h_half_thickness, center[1] + h_half_size]
    h_bottom_left = [center[0] - h_half_thickness, center[1] - h_half_size]
    h_bottom_right = [center[0] - h_half_thickness, center[1] + h_half_size]

    # Corners of the center square
    center_nw = [center[0] + h_half_thickness, center[1] - v_half_thickness]
    center_ne = [center[0] + h_half_thickness, center[1] + v_half_thickness]
    center_sw = [center[0] - h_half_thickness, center[1] - v_half_thickness]
    center_se = [center[0] - h_half_thickness, center[1] + v_half_thickness]

    # Return as a list in the adjusted order
    return [ v_top_left, v_top_right, center_ne, h_top_right, h_bottom_right, center_se, v_bottom_right, v_bottom_left, center_sw, h_bottom_left, h_top_left, center_nw]

def draw_arrow(center, speed, direction):
    speed_modifier = speed
    ws_lat = center[0]
    ws_long = center[1]

    len_scale = 0.00012*200*speed_modifier
    sides_scale = 0.000025*300 * 5
    sides_angle = 20


    latB = len_scale * math.cos(math.radians(direction)) + ws_lat
    longB = len_scale * math.sin(math.radians(direction)) + ws_long

    latC = sides_scale * math.cos(math.radians(direction + 180 - sides_angle)) + latB
    longC = sides_scale * math.sin(math.radians(direction + 180 - sides_angle)) + longB

    latD = sides_scale * math.cos(math.radians(direction + 180 + sides_angle)) + latB
    longD = sides_scale * math.sin(math.radians(direction + 180 + sides_angle)) + longB

    lat_reverse = len_scale * math.cos(math.radians(direction + 180)) + ws_lat
    long_reverse = len_scale * math.sin(math.radians(direction + 180)) + ws_long 

    pointA = (ws_lat, ws_long)
    pointB = (latB, longB)
    pointC = (latC, longC)
    pointD = (latD, longD)
    tail = (lat_reverse, long_reverse)

    point = [pointA, pointB, pointC, pointD, pointB, tail]
    return point

def find_distance(coords1:list[float], coords2:list[float]):
    R = 6373.0
    lat1 = math.radians(coords1[0])
    lon1 = math.radians(coords1[1])
    lat2 = math.radians(coords2[0])
    lon2 = math.radians(coords2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def rainfall_to_color(percipitation):
    light_rainfall = (255, 255, 153)  # RGB for "#FFFF99"
    moderate_rainfall = (173, 216, 230)  # RGB for "#ADD8E6"
    heavy_rainfall = (0, 0, 139)  # RGB for "#00008B"
    # Clamp temperature
    distance = 100 - (percipitation)
    adj_percip = max(0, min(100, distance))
    ratio = 1 - math.log(101 - adj_percip) / math.log(101)

    r = int(moderate_rainfall[0] * (1 - ratio) + light_rainfall[0] * ratio)
    g = int(moderate_rainfall[1] * (1 - ratio) + light_rainfall[1] * ratio)
    b = int(moderate_rainfall[2] * (1 - ratio) + light_rainfall[2] * ratio)

    return f"#{r:02X}{g:02X}{b:02X}"
 
def lerp_color(a, b, t):
    """Interpolate between two RGB colors."""
    ax, ay, az = a
    bx, by, bz = b
    return (
        int(ax + (bx - ax) * t),
        int(ay + (by - ay) * t),
        int(az + (bz - az) * t)
    )

def rainfall_to_opacity(percipitation):
    return min(0.5 + percipitation/100, 1)

def temperature_to_rgb(temp: float) -> tuple[int, int, int]:
    """Converts a temperature value to RGB."""
    # Define color RGB values
    white = (255, 255, 255)
    blue = (0, 0, 255)
    orange = (255, 165, 0)
    
    # Clamp temperature
    temp = max(-10, min(40, temp))

    if temp <= 10:
        temp += 10
        ratio = 1 - math.log(21 - temp) / math.log(21)  # Normalizing to [0, 1] range
        r = int(white[0] * (1 - ratio) + blue[0] * ratio)
        g = int(white[1] * (1 - ratio) + blue[1] * ratio)
        b = int(white[2] * (1 - ratio) + blue[2] * ratio)
    else:
        distance = 40 - (temp-10)
        ratio = 1-math.log(41 - distance) / math.log(31)  
        r = int(orange[0] * (1 - ratio) + blue[0] * ratio)
        g = int(orange[1] * (1 - ratio) + blue[1] * ratio)
        b = int(orange[2] * (1 - ratio) + blue[2] * ratio)

    return f"#{r:02X}{g:02X}{b:02X}"

def add_zone_of_influence(coords, radius, previous_weather, m, heat_map_data):
    mean_temp, percipitation, visibility = previous_weather
    percipitation = float(percipitation)/10
    mean_temp = float(mean_temp)/10

    percip_color = rainfall_to_color(percipitation)
    opacity = rainfall_to_opacity(percipitation)

    temp_color = temperature_to_rgb(mean_temp)
    distance = 89 - float(visibility)
    visibility_modifier = min((1 - math.log(90 - max(1, distance)) / math.log(90)) + 0.1, 1)
    #print(visibility_modifier, visibility)
    heat_map_data.add((coords[0], coords[1], 0.3))
    hmap = HeatMap([(coords[0], coords[1], 0.3)],radius = 30, gradient={0.4: temp_color, 0.65: temp_color, 1: temp_color}, min_opacity=visibility_modifier)#, gradient={0: temp_color, 1: temp_color})
    hmap.add_to(m)
    


    folium.Circle(
    location=coords,
    radius=radius,
    color=percip_color,
    fill=False,
    opacity=opacity,
    popup=f"{mean_temp}°C\n{percipitation}mm\nVis: {visibility}",
    dash_array='10'
    ).add_to(m)

import imageio
if __name__ == "__main__":
#    draw_map()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    images = os.path.join(current_dir, 'images')
    filenames : list[tuple[list]] = [x for x in os.walk(images)][0][2:][0]
    with imageio.get_writer(os.path.join(current_dir, 'final_gif.gif'), mode='I') as writer:
        for filename in filenames:
            image = imageio.imread(os.path.join(current_dir, os.path.join("images", filename)))
            writer.append_data(image)


 