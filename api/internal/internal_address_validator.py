import falcon
import json
import requests
import logging
import time
from security_feature_flags import feature_flags

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CorsMiddleware:
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        resp.set_header('Access-Control-Allow-Headers', 'Content-Type')

    def process_response(self, req, resp, resource, req_succeeded):
        if req.method == 'OPTIONS':
            resp.status = falcon.HTTP_200

class TimeoutException(Exception):
    def __init__(self, message="Request timed out"):
        self.message = message
        super().__init__(self.message)


class ToggleFeatureResource:
    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))
            feature = data['feature']
            enabled = data['enabled']
            if feature_flags.set_flag(feature, enabled):
                logging.info(f"Feature '{feature}' updated to {feature_flags.is_enabled(feature)}")
                resp.media = {"status": "success", "message": f"Feature '{feature}' updated."}
                resp.status = falcon.HTTP_200
            else:
                resp.media = {"status": "error", "message": "Feature not found."}
                resp.status = falcon.HTTP_404
        except Exception as e:
            logging.error("Failed to update feature flag", exc_info=e)
            resp.media = {"status": "error", "message": "Failed to update feature flag"}
            resp.status = falcon.HTTP_500
    def on_get(self, req, resp):
        try:
            resp.media = {"status": "success", "flags": feature_flags.flags}
            resp.status = falcon.HTTP_200
        except Exception as e:
            logging.error("Failed to retrieve feature flags", exc_info=e)
            resp.media = {"status": "error", "message": "Failed to retrieve feature flags"}
            resp.status = falcon.HTTP_500

class AddressValidationResource:
    def __init__(self):
        self.request_count = 0  # Initialize the request counter

    def on_post(self, req, resp):
        if feature_flags.is_enabled('timeouts'):
            self.request_count += 1  # Increment only if timeouts are enabled

        if not feature_flags.check_and_increment_quota():
            resp.media = {
                'status': 'error',
                'message': 'Quota exceeded. Please wait 30 seconds before retrying.'
            }
            resp.status = falcon.HTTP_429
            return

        try:
            address_data = json.loads(req.stream.read().decode('utf-8'))
            if not address_data.get('address'):
                raise falcon.HTTPBadRequest('Invalid request', 'Address field is required.')

            address = address_data['address']
            logging.info(f"Received address: {address}")
            
            # Check if timeouts are enabled and if the request count is a multiple of 5
            wait_time = 5 if feature_flags.is_enabled('timeouts') and self.request_count % 5 == 0 else None
            validated_data = self.validate_address_external(address, wait=wait_time)

            if validated_data:
                logging.info(f"External service response: {validated_data.get('message')}")
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
                
        except TimeoutException as e:
            logging.error(f"Timeout occurred: {str(e)}")
            resp.media = {
                'status': 'error',
                'message': str(e)
            }
            resp.status = falcon.HTTP_400  # HTTP 408 Request Timeout

        except ValueError:
            logging.error("Malformed JSON received")
            raise falcon.HTTPError(falcon.HTTP_400, 'Malformed JSON')

    def validate_address_external(self, address, wait=None):
        if wait is not None:
            url = f'http://127.0.0.1:8001/validate?wait={wait}'
        else:
            url = 'http://127.0.0.1:8001/validate'
        
        try:
            response = requests.post(url, json={'address': address}, timeout=3)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"External service returned HTTP {response.status_code}")
                return None
            
        except requests.exceptions.Timeout:
            logging.error("The request timed out after 3 seconds")
            raise TimeoutException("The request timed out after 3 seconds")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error contacting external service: {e}")
            return None

app = falcon.App(middleware=[CorsMiddleware()])
app.add_route('/validate', AddressValidationResource())
app.add_route('/toggle-feature', ToggleFeatureResource())
