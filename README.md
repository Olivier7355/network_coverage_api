# Network coverage API by providers in France
API that we can request with a textual address request and retrieve 2G/3G/4G network coverage for each operator in France.

## Usage
- Query parameter: q
- GET: http://127.0.0.1:8000/network_coverage?q=29+Jardins+Boieldieu+92800+Puteaux

## Screenshots
### Pytest test functions result:
![pytest](https://github.com/Olivier7355/network_coverage_api/assets/108932082/54d3377c-2ff2-4c35-9683-76a58b49a856)
  
### Calling the endpoint with a correct address:
![all_ok](https://github.com/Olivier7355/network_coverage_api/assets/108932082/2caf98f0-a5aa-4610-b7f1-8eff8c9ceccb)
  
### Calling the endpoint when the 'api-adresse.data.gouv.fr' API return more than one address:
![more_address](https://github.com/Olivier7355/network_coverage_api/assets/108932082/1f0cdd5f-c266-4030-acea-d8c2ce607a07)
  
### Calling the endpoint when the address is not provided:
![no_address](https://github.com/Olivier7355/network_coverage_api/assets/108932082/6c078826-c87c-47e1-a283-432646e5c76d)
  
### Calling the endpoint with an unknown address:
![unknown](https://github.com/Olivier7355/network_coverage_api/assets/108932082/9c8624f0-da75-40fe-936e-d6994694bb6c)

