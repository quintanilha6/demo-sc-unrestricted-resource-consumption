import falcon
import json
import requests
import logging
import re
import time
from security_feature_flags import feature_flags
from threading import Semaphore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
cache = {}

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
        super().__init__(message)

class InputValidationException(Exception):
    def __init__(self, message="Input is not valid"):
        super().__init__(message)

class ConcurrencyLimitException(Exception):
    def __init__(self, message="Concurrency limit exceeded"):
        super().__init__(message)

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
    def __init__(self, concurrency_limit=5):
        self.semaphore = Semaphore(concurrency_limit)  # Initialize the semaphore with the concurrency limit

    def on_post(self, req, resp):
        logging.info("Request received")

        # Check if concurrency limits are enabled
        if feature_flags.is_enabled('concurrency'):
            logging.info("Concurrency feature is enabled")
            # Attempt to acquire the semaphore
            if not self.semaphore.acquire(blocking=False):
                logging.error("Concurrency limit exceeded")
                resp.media = {
                    'status': 'error',
                    'message': 'Concurrency limit exceeded'
                }
                resp.status = falcon.HTTP_429
                return
            logging.info("Semaphore acquired, current count: %d", self.semaphore._value)

        try:
            address_data = json.loads(req.stream.read().decode('utf-8'))
            
            
            # Address Validation

            # Address Validation
            if feature_flags.is_enabled('inputValidation'):
                if not address_data.get('address'):
                    raise InputValidationException("Address input is required")
                if not self.validate_address_input(address_data['address']):
                    raise InputValidationException("Address input is not valid.")

            address = address_data['address']
            logging.info(f"Received address: {address}")

            # Simulate processing delay
            time.sleep(2)

            if feature_flags.is_enabled('efficiency'):
                cached_result = self.get_cached_address(address)
                if cached_result:
                    logging.info(f"Cache hit for address: {address}")
                    resp.media = {
                        'status': 'success',
                        'validation': cached_result.get('validation'),
                        'message': cached_result.get('message')
                    }
                    resp.status = falcon.HTTP_200
                    return

            validated_data = self.validate_address_external(address)

            if validated_data:
                logging.info(f"External service response: {validated_data.get('message')}")
                if feature_flags.is_enabled('efficiency'):
                    self.cache_validated_address(address, validated_data)
                    resp.media = {
                        'status': 'success',
                        'validation': validated_data.get('validation'),
                        'message': validated_data.get('message')
                    }
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

        except InputValidationException as e:
            logging.error(f"{str(e)}")
            resp.media = {
                'status': 'error',
                'message': str(e)
            }
            resp.status = falcon.HTTP_400

        except TimeoutException as e:
            logging.error(f"Timeout occurred: {str(e)}")
            resp.media = {
                'status': 'error',
                'message': str(e)
            }
            resp.status = falcon.HTTP_400

        finally:
            # Always release the semaphore if concurrency is enabled
            if feature_flags.is_enabled('concurrency'):
                self.semaphore.release()
                logging.info("Semaphore released, current count: %d", self.semaphore._value)

    def validate_address_input(self, address):
        address = address.strip()
        pattern = re.compile(r'^[a-zA-Z0-9 ,.-]+$')
        return pattern.match(address) is not None
    
    def validate_address_external(self, address, wait=None):
        if wait is not None:
            url = f'http://external_api:8001/validate?wait={wait}'
        else:
            url = 'http://external_api:8001/validate'
        
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

    def get_cached_address(self, address):
        return cache.get(address)

    def cache_validated_address(self, address, data):
        cache[address] = data

app = falcon.App(middleware=[CorsMiddleware()])
app.add_route('/validate', AddressValidationResource(concurrency_limit=5))
app.add_route('/toggle-feature', ToggleFeatureResource())
