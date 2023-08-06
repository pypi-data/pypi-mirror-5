from mock import patch

from pyramid_facebook.lib import encrypt_signed_request

__all__ = ['conf', 'get_signed_request']

conf = {
    'facebook.app_id': '1234567890',
    'facebook.secret_key': 'abcdef1234567890',
    'facebook.namespace': 'test_canvas',
    'facebook.scope': 'publish_actions,email',
    'pyramid.debug_routematch': True,
    }


def get_signed_request(**params):
    return encrypt_signed_request(conf['facebook.secret_key'], params)


def setup_package():
    patch('pyramid_facebook.security.get_application_access_token').start()
