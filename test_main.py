from fastapi.testclient import TestClient
from main import app, retrieve_geographic_coordinates, get_network_coverage_data

client = TestClient(app)

# Test the API endpoint

def test_valid_query_address():
    response = client.get('/network_coverage/?q=20+avenue+de+Segur+Paris')
    assert response.status_code == 200
    assert  response.json() == {
                                'Bouygue': {'2G': True, '3G': True, '4G': True}, 
                                'Free': {'2G': False, '3G': True, '4G': False}, 
                                'Orange': {'2G': False, '3G': False, '4G': False}, 
                                'SFR': {'2G': True, '3G': True, '4G': False}
                                }


def test_uncomplete_query_address():
    response = client.get('/network_coverage/?q=29+Jardins')
    assert response.status_code == 200
    assert response.json() == {"message":"data.gouv.fr API found more than one address. Refine your query."}
    

def test_no_query_address():
    response = client.get('/network_coverage/?q=')
    assert response.status_code == 200
    assert response.json() == {"message":"No address provided. Please include 'q' parameter in the query."}


# Test the data retrieval functions

def test_retrieve_geographic_coordinates():
    result = retrieve_geographic_coordinates('29+Jardins+Boieldieu+92800+Puteaux')
    assert len(result) == 3
    assert result[0] == 644120.77
    assert result[1] == 6865693.58 
    assert result[2] == 'Puteaux'


def test_get_network_coverage_data():
    result = get_network_coverage_data('Paris')
    assert result == {
                        'Orange': {'2G': False, '3G': False, '4G': False}, 
                        'SFR': {'2G': True, '3G': True, '4G': False}, 
                        'Free': {'2G': False, '3G': True, '4G': False}, 
                        'Bouygue': {'2G': True, '3G': True, '4G': True}
                        }


