"""
API script that, for a given address in France, retrieves the 2G/3G/4G network coverage for each operator (city-level precision).

Example: http://127.0.0.1:8000/network_coverage/?q=20+avenue+de+Segur+Paris
Response: {
            "Orange":{"2G":false,"3G":false,"4G":false},
            "SFR":{"2G":true,"3G":true,"4G":false},
            "Free":{"2G":false,"3G":true,"4G":false},
            "Bouygue":{"2G":true,"3G":true,"4G":true}
            }
"""

import csv
import json
import requests
from fastapi import FastAPI, Query

app = FastAPI()

# Custom exceptions
class ClientError(Exception):
    pass
class ServerError(Exception):
    pass
class APIConnectionError(Exception):
    pass
class APIFindMoreThanOneAddressError(Exception):
    pass
class APICityMissingError(Exception):
    pass
class APINoAddressFoundError(Exception):
    pass
class DBCityNotFoundError(Exception):
    pass

# Create the API endpoint
@app.get('/network_coverage/')
def get_network_coverage(q: str = Query(..., title="Address")) -> dict :
    if not q :
        return {"message": "No address provided. Please include 'q' parameter in the query."}
    
    try :
        # Function call that connect to data.gouv.fr API and extract the longitude, latitude 
        # and city from the address 'q'.
        # 'gps_longitude' and 'gps_latitude' are not used in this script since we use a 
        # city-level precision but will be usefull if more precision is needed.
        gps_longitude, gps_latitude, city = retrieve_geographic_coordinates(q)

        # Function call that search in 'network_coverage_by_city.csv' for the city and retrieves 
        # the providers, 2G, 3G and 4G coverage.    
        payload = get_network_coverage_data(city)

    except ClientError :
        return {"message": "Client Error."}
    except ServerError :
        return {"message": "Server Error."}
    except APIConnectionError :
        return {"message": "Unable to connect to data.gouv.fr API."}
    except APINoAddressFoundError :
        return {"message": "data.gouv.fr API can\'t find any address. Refine your query."}
    except APIFindMoreThanOneAddressError :
        return {'message': 'data.gouv.fr API found more than one address. Refine your query.'}
    except APICityMissingError :
        return {'message': 'data.gouv.fr API can\'t find the city name. Refine your query.'}
    except DBCityNotFoundError :
        return {'message': 'The city can\'t be found in the network coverage database.'}

    return payload


# Extract latitude, longitude and city from https://api-adresse.data.gouv.fr
def retrieve_geographic_coordinates(address : str) -> tuple :
    try :
        response = requests.get(f"https://api-adresse.data.gouv.fr/search/?q={address}&type=housenumber&autocomplete=1")
        response.raise_for_status()
    
    except requests.exceptions.HTTPError :
        if 400 <= response.status_code < 500:
            raise ClientError()
        elif 500 <= response.status_code < 600:
            raise ServerError()
        else :
            raise APIConnectionError()
        
    geojson_data = response.text
    data = json.loads(geojson_data)

    # Check if data.gouv.fr API retruns exactly one address.
    if not data['features'] :
        raise APINoAddressFoundError()
    elif len(data['features']) > 1 :
        raise APIFindMoreThanOneAddressError()
    
    gps_longitude = data['features'][0]['properties']['x']
    gps_latitude = data['features'][0]['properties']['y']
    city = data["features"][0]["properties"]["city"]

    # We can't find any network coverage if data.gouv.fr API does not return a city name.
    if city is None :
        raise APICityMissingError()
                                         
    return (gps_longitude, gps_latitude, city)
    

# Search for the city in 'network_coverage_by_city.csv' and retrieve the 2G, 3G and 4G coverage information
def get_network_coverage_data(city : str) -> dict :
    filtered_rows = []
    payload = {}
    
    # Retrieve the lines from the csv that contains only the inquired city.
    with open('network_coverage_by_city.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader :
            if row[-1] == city :
                filtered_rows.append(row)

    if len(filtered_rows) == 0 :
        raise DBCityNotFoundError()

    # Format a dict that will contain all the requested information for the API endpoint payload
    for row in filtered_rows:
        provider = row[0]
        if provider not in payload:
            payload[provider] = {'2G': False if row[3] == '0' else True, 
                                 '3G': False if row[4] == '0' else True,
                                 '4G': False if row[5] == '0' else True
                                 }

    return payload


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
