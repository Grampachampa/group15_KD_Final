import os
import csv

# station dict
station_dict = {
    209: 'IJmond',
    210: 'Valkenburg Zh',
    215: 'Voorschoten',
    225: 'IJmuiden',
    229: 'Texelhors',
    235: 'De Kooy',
    240: 'Schiphol',
    242: 'Vlieland',
    248: 'Wijdenes',
    249: 'Birch wood',
    251: 'Hoorn Terschelling',
    257: 'Wijk aan Zee',
    258: 'Houtribdijk',
    260: 'De Bilt',
    265: 'Soesterberg',
    267: 'Stavoren',
    269: 'Lelystad',
    270: 'Leeuwarden',
    273: 'Marknesse',
    275: 'Share',
    277: 'Lauwersoog',
    278: 'Heino',
    279: 'Hoogeveen',
    280: 'Elde',
    283: 'Hopsel',
    285: 'Huibertgat',
    286: 'New Beerta',
    290: 'Twenthe',
    308: 'Cadzand',
    310: 'Vlissingen',
    311: 'Main plate',
    312: 'Oosterschelde',
    313: 'Plain of De Raan',
    315: 'Hansweert',
    316: 'Pair of scissors',
    319: 'Westdorpe',
    323: 'Wilhelminadorp',
    324: 'Stavenisse',
    330: 'Hoek van Holland',
    331: 'Tholen',
    340: 'Woensdrecht',
    343: 'Rotterdam Geulhaven',
    344: 'Rotterdam',
    348: 'Cabauw Mast',
    350: 'Gilze-Rijen',
    356: 'Herwijnen',
    370: 'Eindhoven',
    375: 'Volkel',
    377: 'Ell',
    380: 'Maastricht',
    391: 'Arcen'
}

# Get the full path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define the input and output file paths
input_file = os.path.join(current_dir, 'nl_weather_data.txt')
output_file = os.path.join(current_dir, 'nl_weather_data.csv')

# Read the input file and convert it to a list of lines
rows = []
with open(output_file, 'w') as csvfile:
    with open(input_file, 'r') as f:
        dictreader = csv.DictReader(f, skipinitialspace=True)
        counter = 0
        for row in dictreader:
            for cell, element in row.items():
                row[cell] = element.strip()
            
            row["NAME"] = station_dict[int(row["STN"])]

            if counter == 0:
                rows.append([i for i in row])
            
            rows.append([i if i != ''  else "  " for j, i in row.items()])

            
            counter +=1
            # if counter >3:
            #     break

    writer_object = csv.writer(csvfile, lineterminator="\n")
    for row in rows:
        writer_object.writerow(row)

        

