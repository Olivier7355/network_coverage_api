"""
This script converts the Input file into the Output file which will serve as the database for the API (main.py).

Input file : 2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv

Operateur;x;y;2G;3G;4G
20801;102980;6847973;1;1;0
20810;103113;6848661;1;1;0
20820;103114;6848664;1;1;1
20801;112032;6840427;0;1;1

Output file : network_coverage_by_city.csv

provider,lon,lat,2G,3G,4G,city
Orange,-5.08885611530134,48.4565745588299,1,1,0,Ouessant
SFR,-5.088018169414725,48.46285384829353,1,1,0,Ouessant
Bouygue,-5.088008862939314,48.46288161522891,1,1,1,Ouessant
Orange,-4.956781637814166,48.39729748137953,0,1,1,Île-Molène
"""

import csv
import pyproj
import requests

# Convert from Lambert 93 to GPS coordinates
def lamber93_to_gps(lambert_x : int, lambert_y : int) -> tuple[float] :
	lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
	wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
	long, lat = pyproj.transform(lambert, wgs84, lambert_x, lambert_y)
	return (long, lat)


# Generate a 'temp.csv' file with the columns 'provider','lon','lat','2G','3G','4G'
def create_file_with_longitude_and_latitude():
    data_array = []
    providers = {'20801':'Orange',
                '20810':'SFR',
                '20815':'Free',
                '20820':'Bouygue'}
    
    with open('2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        next(csvreader)
        for row in csvreader:     
            row[0] = providers[row[0]]
            row[1], row[2] = lamber93_to_gps(row[1], row[2])
            data_array.append(row)
    
    # Write the processed rows to 'temp.csv'
    with open('temp.csv', mode='w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        csvwriter.writerow(['provider','lon','lat','2G','3G','4G'])
        csvwriter.writerows(data_array)


# Call the 'api-adresse.data.gouv.fr' API to find the cities coresponding to 
# the coordinates in the 'temp.csv' file and save the result into 'network_coverage_by_city.csv'
def get_city_from_gps_coord():
    # Warning : 'api-adresse.data.gouv.fr' API cannot process files bigger than 6Mb.
    response = requests.post('https://api-adresse.data.gouv.fr/reverse/csv/', files={'data': open('./temp.csv', 'rb')})
    csv_data = response.text

    # Parse the CSV response data from 'api-adresse.data.gouv.fr' API
    csv_reader = csv.reader(csv_data.splitlines(), delimiter=',')
    next(csv_reader)
    processed_rows = []
    for row in csv_reader:

        # Keep only the columns 'Provider', 'lon', 'lat', '2G', '3G', '4G' and 'City' 
        new_row = row[0:6]+[row[16]]
        processed_rows.append(new_row)
    
    # Save the processed rows to 'network_coverage_by_city.csv'
    with open('network_coverage_by_city.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['Provider','lon','lat','2G','3G','4G','City'])
        csv_writer.writerows(processed_rows)


if __name__ == "__main__":
    # Function call that generates a 'temp.csv' file with the columns 'provider','lon','lat','2G','3G','4G'.
    create_file_with_longitude_and_latitude()
    
    # Function call that, from 'lon' and 'lat', find the city provided by 'api-adresse.data.gouv.fr' API.
    get_city_from_gps_coord()
    