import falcon
import json
import requests
import logging
import time

# CORS Middleware to allow cross-origin requests
class CorsMiddleware:
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        resp.set_header('Access-Control-Allow-Headers', 'Content-Type')

    def process_response(self, req, resp, resource, req_succeeded):
        if req.method == 'OPTIONS':
            resp.status = falcon.HTTP_200

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AddressValidationResource:
    def on_post(self, req, resp):
        try:
            address_data = json.loads(req.stream.read().decode('utf-8'))
        except ValueError:
            logging.error("Malformed JSON received")
            raise falcon.HTTPError(falcon.HTTP_400, 'Malformed JSON')

        if not address_data.get('address'):
            logging.error("No address provided in request")
            raise falcon.HTTPBadRequest('Invalid request', 'Address field is required.')

        address = address_data['address']

        logging.info(f"Received address: {address}")
        logging.info(f"Sending address to external service for validation: {address}")
        
        time.sleep(0.25)  # Simulate some latency
        validated_data = self.validate_address_external(address)
        time.sleep(0.25)  # Simulate some latency

        if validated_data:
            logging.info(f"External service response: {validated_data.get('message')}\n")
            resp.media = {
                'status': 'success',
                'validation': validated_data.get('validation'),
                'message': validated_data.get('message')
            }
            resp.status = falcon.HTTP_200
        else:
            logging.error("Failed to validate address with external service")
            resp.media = {
                'status': 'failure',
                'message': 'Failed to validate address with external service'
            }
            resp.status = falcon.HTTP_500

    def validate_address_external(self, address):
        url = 'http://127.0.0.1:8001/validate'
        try:
            response = requests.post(url, json={'address': address})
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"External service returned HTTP {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error contacting external service: {e}")
            return None

app = falcon.App(middleware=[CorsMiddleware()])
app.add_route('/validate', AddressValidationResource())