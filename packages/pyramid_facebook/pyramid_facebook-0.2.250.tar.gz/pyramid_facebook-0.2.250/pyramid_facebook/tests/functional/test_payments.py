from decimal import Decimal

import mock
from facepy.signed_request import SignedRequestError

from pyramid_facebook.tests.functional import TestView


class TestFacebookPayments(TestView):

    @mock.patch('requests.get')
    @mock.patch('pyramid_facebook.payments.get_application_access_token')
    @mock.patch('facepy.SignedRequest.parse')
    def test_put_order(self, m_sreq_parse, m_get_app_token, m_http_get):
        # https://developers.facebook.com/docs/howtos/payments/fulfillment/
        m_sreq_parse.return_value = {
            'algorithm': 'HMAC-SHA256',
            'issued_at': 1367617646,
            'payment_id': 370022,
            'quantity': 1,
            'status': 'completed',
        }
        m_http_get.return_value.json.return_value = {
            'id': '370022',
            'user': {
                'id': '123',
                'name': 'Peter',
            },
            'application': {
                'name': 'Yo App',
                'namespace': 'yo_app_tests',
                'id': '555999',
            },
            'actions': [
                {
                    'type': 'charge',
                    'status': 'completed',
                    'currency': 'GBP',
                    'amount': '0.05',
                    'time_created': '2013-05-14T05:35:24+0000',
                    'time_updated': '2013-05-14T05:35:24+0000',
                },
            ],
            'refundable_amount': {
                'currency': 'GBP',
                'amount': '0.05',
            },
            'items': [
                {
                    'type': 'IN_APP_PURCHASE',
                    'product': 'http:/example.com/og/pack',
                    'quantity': 1,
                },
            ],
            'country': 'GB',
            'created_time': '2013-05-14T05:35:24+0000',
            'payout_foreign_exchange_rate': Decimal('1.5124725'),
        }

        resp = self.app.put('/test_canvas/orders/370022',
                            params={'signed_request': 'fake'}, status=200)

        self.assertEqual(resp.body, 'completed')

    @mock.patch('facepy.SignedRequest.parse')
    def test_put_order_invalid_signed_request(self, m_sreq_parse):
        m_sreq_parse.side_effect = SignedRequestError('Nope')

        self.app.put('/test_canvas/orders/380088',
                     params={'signed_request': 'fake'}, status=400)

    @mock.patch('facepy.SignedRequest.parse')
    def test_put_order_invalid_payment_id(self, m_sreq_parse):
        m_sreq_parse.return_value = {
            'algorithm': 'HMAC-SHA256',
            'issued_at': 1367617646,
            'payment_id': 360066,
            'quantity': 1,
            'status': 'completed',
        }

        self.app.put('/test_canvas/orders/30055',
                     params={'signed_request': 'fake'}, status=400)
