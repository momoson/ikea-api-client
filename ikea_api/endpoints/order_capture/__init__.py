from ...api import API
from ...utils import validate_zip_code
from ...errors import WrongZipCodeError, NoDeliveryOptionsAvailableError
from ..cart import Cart


class OrderCapture(API):
    """
    API responsible for making an order.
    Use case — check available delivery services.
    """

    def __init__(self, token, zip_code):
        super().__init__(token, 'https://ordercapture.ikea.ru/ordercaptureapi/ru')

        if self.country_code != 'ru':
            self.endpoint = 'https://ordercapture.ingka.com/ordercaptureapi/{}'.format(
                self.country_code)

        zip_code = str(zip_code)
        validate_zip_code(zip_code)
        self.zip_code = zip_code

        self.session.headers['X-Client-Id'] = 'af2525c3-1779-49be-8d7d-adf32cac1934'

    def error_handler(self, status_code, response_json):
        if 'errorCode' in response_json:
            error_code = response_json['errorCode']
            if error_code == 60004:
                raise WrongZipCodeError
            elif error_code == 60005 or error_code == 60006:
                raise NoDeliveryOptionsAvailableError

    def _get_items_for_checkout_request(self):
        cart = Cart(self.token)
        cart_show = cart.show()
        items_templated = []
        try:
            if cart_show.get('data'):
                for d in cart_show['data']['cart']['items']:
                    items_templated.append({
                        'quantity': d['quantity'],
                        'itemNo': d['itemNo'],
                        'uom': d['product']['unitCode']

                    })
        except KeyError:
            pass
        return items_templated

    def _get_checkout(self):
        items = self._get_items_for_checkout_request()
        if len(items) == 0:
            return

        data = {
            'shoppingType': 'ONLINE',
            'channel': 'WEBAPP',
            'checkoutType': 'STANDARD',
            'languageCode': 'ru',
            'items': items,
            'deliveryArea': None
        }

        response = self.call_api(
            endpoint='{}/checkouts'.format(self.endpoint),
            headers={'X-Client-Id': '6a38e438-0bbb-4d4f-bc55-eb314c2e8e23'},
            data=data)

        if 'resourceId' in response:
            return response['resourceId']
        else:
            raise Exception('No resourceId for checkout')

    def _get_delivery_area(self, checkout):
        response = self.call_api(
            endpoint='{}/checkouts/{}/delivery-areas'.format(
                self.endpoint, checkout),
            data={
                'zipCode': self.zip_code,
                'enableRangeOfDays': False
            })

        if 'resourceId' in response:
            return response['resourceId']
        else:
            raise Exception('No resourceId for delivery area')

    def get_delivery_services(self):
        checkout = self._get_checkout()
        delivery_area = self._get_delivery_area(checkout)

        response = self.call_api(
            '{}/checkouts/{}/delivery-areas/{}/delivery-services'
            .format(self.endpoint, checkout, delivery_area))
        return response
