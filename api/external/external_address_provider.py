import falcon
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ExternalAddressProvider:
    price_to_charge = 0.00

    def __init__(self):
        self.addresses = [
            "Main Street", "Main Avenue", "Maple Street", "Elm Street", "Oak Avenue", "Pine Street",
            "Urb. dos Camarinhos", "Rua da fonte", "Impasse de Fougeres", "Travessa da Encosta"
            "Impasse des Fougeres", "Impasse des Alpes", "Cherry Lane", "Cherry Court",
            "Orchard Road", "Grove Lane", "Forest Drive", "Hill Valley", "Summer Road",
            "River Road", "Lake Avenue", "Winter Lane", "Spring Street", "Autumn Road",
            "Park Avenue", "Cedar Lane", "Aspen Drive", "Vine Street", "Rose Lane",
            "Lily Road", "Daisy Drive", "Hyacinth Drive", "Sunflower Lane", "Tulip Street",
            "Magnolia Avenue", "Holly Drive", "Jasmine Lane", "Fern Street", "Birch Road",
            "Walnut Street", "Peach Road", "Apple Lane", "Pear Street", "Cherry Boulevard",
            "Orange Avenue", "Banana Drive", "Grape Road", "Lemon Lane", "Plum Street",
            "Watermelon Drive", "Kiwi Lane", "Mango Street", "Apricot Avenue", "Papaya Drive",
            "Coconut Lane", "Pineapple Street", "Melon Road", "Strawberry Lane", "Raspberry Street",
            "Blueberry Avenue", "Blackberry Lane", "Nectarine Street", "Grapefruit Road", "Lime Lane",
            "Fig Street", "Almond Drive", "Chestnut Lane", "Hazelnut Street", "Macadamia Road",
            "Pecan Lane", "Brazil Nut Street", "Pistachio Drive", "Cashew Lane", "Walnut Street",
            "Beech Road", "Sycamore Street", "Poplar Lane", "Cypress Drive", "Alder Street",
            "Willow Lane", "Teak Road", "Bamboo Street", "Pine Drive", "Sequoia Lane",
            "Cedar Street", "Oak Drive", "Maple Lane", "Aspen Street", "Fir Road",
            "Elm Lane", "Birch Street", "Cherry Road", "Peach Lane", "Pear Drive",
            "Orange Street", "Lemon Lane", "Plum Road", "Apricot Street", "Apple Drive",
            "Mango Lane", "Banana Street", "Coconut Road", "Pineapple Lane", "Melon Drive"
        ]

    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read().decode('utf-8'))
            query_string = data.get('address')
        except (ValueError, KeyError):
            logging.error("Malformed request or missing 'address' field")
            resp.status = falcon.HTTP_400
            resp.media = {'error': 'Malformed request, address field missing or bad JSON'}
            return

        if not query_string:
            logging.error("Received empty query for address validation")
            resp.status = falcon.HTTP_400
            resp.media = {'error': 'Address field is required'}
            return

        logging.info(f"Received address for validation: {query_string}")
        # Check if the address is in the database
        if query_string in self.addresses:
            validation = True
            message = "Address is valid."
        else:
            validation = False
            message = "Address is not valid."

        logging.info(f"Validation result for {query_string}: {message}")

        self.price_to_charge += 0.01
        logging.info(f"Charging client 0.01 CHF. Total to be charged at the end of the month: {self.price_to_charge:.2f} CHF\n")

        resp.media = {
            'validation': validation,
            'message': message
        }
        resp.status = falcon.HTTP_200

app = falcon.App()
app.add_route('/validate', ExternalAddressProvider())