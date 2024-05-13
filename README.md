# demo-sc-unrestricted-resource-consumption
To do
install req 

cd for the right palces
gunicorn -b 127.0.0.1:8000 internal_address_validator:app
gunicorn -b 127.0.0.1:8000 external_address_provider:app

cd to ui
python -m http.server 8080

next steps .. make feature flags that activate the security 