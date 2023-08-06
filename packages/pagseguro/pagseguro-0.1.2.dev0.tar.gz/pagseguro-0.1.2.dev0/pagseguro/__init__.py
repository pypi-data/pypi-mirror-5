# coding: utf-8
import requests
import xmltodict

from .configs import Config
from .utils import parse_date, is_valid_email, is_valid_cpf


class PagSeguroNotificationResponse(object):
    def __init__(self, xml, config=None):
        self.xml = xml
        self.config = config or {}
        self.parse_xml(xml)

    def parse_xml(self, xml):
        parsed = xmltodict.parse(xml)
        transaction = parsed['transaction']
        for k, v in transaction.iteritems():
            setattr(self, k, v)


class PagSeguroCheckoutResponse(object):
    def __init__(self, xml, config=None):
        self.xml = xml
        self.config = config or {}
        self.code = None
        self.date = None
        self.errors = None
        self.payment_url = None
        self.parse_xml(xml)

    def parse_xml(self, xml):
        """ parse returned data """
        parsed = xmltodict.parse(xml)
        if 'errors' in parsed:
            self.errors = parsed['errors']['error']
            return

        checkout = parsed['checkout']
        self.code = checkout['code']
        self.date = parse_date(checkout['date'])

        self.payment_url = self.config.PAYMENT_URL % self.code


class PagSeguro(object):
    """ Pag Seguro V2 wrapper """

    PAC = 1
    SEDEX = 2
    NONE = 3

    def __init__(self, email, token, data=None):
        self.config = Config()
        self.data = {}
        self.data['email'] = email
        self.data['token'] = token
        self.data['currency'] = self.config.CURRENCY

        if data and isinstance(data, dict):
            self.data.update(data)

        self.items = []
        self.sender = {}
        self.shipping = {}
        self._reference = ""
        self.extra_amount = None
        self.redirect_url = None
        self.notification_url = None
        self.abandon_url = None

    def build_checkout_params(self):
        """ build a dict with params """
        params = {}
        if self.sender:
            params['senderName'] = self.sender.get('name')
            params['senderAreaCode'] = self.sender.get('area_code')
            params['senderPhone'] = self.sender.get('phone')
            params['senderEmail'] = is_valid_email(self.sender.get('email'))
            params['senderCPF'] = is_valid_cpf(self.sender.get('cpf'))
            params['senderBornDate'] = self.sender.get('born_date')

        if self.shipping:
            params['shippingType'] = self.shipping.get('type')
            params['shippingAddressStreet'] = self.shipping.get('street')
            params['shippingAddressNumber'] = self.shipping.get('number')
            params['shippingAddressComplement'] = self.shipping.get(
                'complement'
            )
            params['shippingAddressDistrict'] = self.shipping.get('district')
            params['shippingAddressPostalCode'] = self.shipping.get(
                'postal_code'
            )
            params['shippingAddressCity'] = self.shipping.get('city')
            params['shippingAddressState'] = self.shipping.get('state')
            params['shippingAddressCountry'] = self.shipping.get('country',
                                                                 'BRA')

        if self.shipping and self.shipping.get('cost'):
            params['shippingCost'] = self.shipping.get('cost')

        if self.extra_amount:
            params['extraAmount'] = self.extra_amount

        params['reference'] = self.reference

        if self.redirect_url:
            params['redirectURL'] = self.redirect_url

        if self.notification_url:
            params['notificationURL'] = self.notification_url

        if self.abandon_url:
            params['abandonURL'] = self.abandon_url

        for i, item in enumerate(self.items, 1):
            params['itemId%s' % i] = item.get('id')
            params['itemDescription%s' % i] = item.get('description')
            params['itemAmount%s' % i] = item.get('amount')
            params['itemQuantity%s' % i] = item.get('quantity')
            params['itemWeight%s' % i] = item.get('weight')
            params['itemShippingCost%s' % i] = item.get('shipping_cost')

        self.data.update(params)
        self.clean_none_params()

    def clean_none_params(self):
        copy = dict(self.data)
        for k, v in copy.iteritems():
            if not v:
                del self.data[k]

    @property
    def reference_prefix(self):
        return self.config.REFERENCE_PREFIX or "%s"

    @reference_prefix.setter
    def reference_prefix(self, value):
        self.config.REFERENCE_PREFIX = (value or "") + "%s"

    @property
    def reference(self):
        return self.reference_prefix % self._reference

    @reference.setter
    def reference(self, value):
        if not isinstance(value, (str, unicode)):
            value = str(value)
        if value.startswith(self.reference_prefix):
            value = value[len(self.reference_prefix):]
        self._reference = value

    def get(self, url):
        """ do a get transaction """
        return requests.get(url, params=self.data, headers=self.config.HEADERS)

    def post(self, url):
        """ do a post request """
        return requests.post(url, data=self.data, headers=self.config.HEADERS)

    def checkout(self):
        """ create a pagseguro checkout """
        self.build_checkout_params()
        response = self.post(url=self.config.CHECKOUT_URL)
        return PagSeguroCheckoutResponse(response.content, config=self.config)

    def check_notification(self, code):
        """ check a notification by its code """
        response = self.get(url=self.config.NOTIFICATION_URL % code)
        return PagSeguroNotificationResponse(response.content, self.config)

    def add_item(self, **kwargs):
        self.items.append(kwargs)
