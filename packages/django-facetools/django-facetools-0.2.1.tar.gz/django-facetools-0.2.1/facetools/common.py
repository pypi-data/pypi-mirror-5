from datetime import datetime
import base64
import hmac
import hashlib
import time

from django.conf import settings
from facetools import json

def _get_app_access_token(app_id=None, app_secret=None):
    """
    Creates the app access token using either specified Facebook app settings
    or the FACEBOOK_XXX variables defined in settings.py

    Arguments:
    app_id -- The application ID.  Defaults to FACBEOOK_APPLICATION_ID from settings
    app_secret -- The app's secret key.  Defaults to FACEBOOK_APPLICATION_SECRET_KEY from settings.
    """
    if app_id is None:
        app_id = settings.FACEBOOK_APPLICATION_ID
    if app_secret is None:
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
    return '%s|%s' % (app_id, app_secret)

def _create_permissions_string(permission_list):
    """
    Creates an list of individual facebook permissions
    and makes a comma seperated string of permissions.
    """
    return ','.join(permission_list).replace(" ", "")

def _get_facetools_test_fixture_name(app_name):
    return "facetools_test_users_%s.json" % app_name

# ---------------------------------------------------------------------
# Following code originally by Reik Schatz. Taken from Fandjango. Thanks Reik!
# http://javasplitter.blogspot.com/
# https://github.com/reikje
# ---------------------------------------------------------------------

def _parse_signed_request(signed_request, app_secret):
    """Return dictionary with signed request data."""
    try:
        l = signed_request.split('.', 2)
        encoded_sig = str(l[0])
        payload = str(l[1])
    except IndexError:
        raise ValueError("Signed request malformed")

    sig = base64.urlsafe_b64decode(encoded_sig + "=" * ((4 - len(encoded_sig) % 4) % 4))
    data = base64.urlsafe_b64decode(payload + "=" * ((4 - len(payload) % 4) % 4))

    data = json.loads(data)

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        raise ValueError("Signed request is using an unknown algorithm")
    else:
        expected_sig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
        raise ValueError("Signed request signature mismatch")
    else:
        return data

def _create_signed_request(app_secret, user_id=1, issued_at=None, oauth_token=None, expires=None, app_data=None, page=None, add_default_data=True):
    """
    Returns a string that is a valid signed_request parameter specified by Facebook
    see: http://developers.facebook.com/docs/authentication/signed_request/

    Arguments:
    app_secret -- the secret key that Facebook assigns to each Facebook application
    user_id -- optional a long representing the Facebook user identifier (UID) of a user
    issued_at -- optional an int or a datetime representing a timestamp when the request was signed
    oauth_token -- optional a String token to pass in to the Facebook graph api
    expires -- optional an int or a datetime representing a timestamp at which the oauth token expires
    app_data -- optional a dict containing additional application data
    page -- optional a dict having the keys id (string), liked (boolean) if the user has liked the page and optionally admin (boolean) if the user is an admin of that page.

    Regardless of which arguments are given, the encoded JSON object will always contain the following properties:
        -- user_id
        -- algorithm
        -- issued_at

    Examples:
        _create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY)
        _create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, user_id=199)
        _create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, user_id=199, issued_at=1254459600)

    """
    payload = {
        'user_id': user_id,
        'algorithm': 'HMAC-SHA256',
    }
    if add_default_data:
        payload['expires'] = 0
        payload['user'] = {
            'country': 'us',
            'locale': 'en_US',
            'age': {
                'min': 0,
                'max': 150
            }
        }

    value = int(time.time())
    if issued_at is not None and (isinstance(issued_at, datetime) or isinstance(issued_at, int)):
        value = issued_at
        if isinstance(issued_at, datetime):
            value = int(time.mktime(issued_at.timetuple()))
    payload['issued_at'] = value

    if oauth_token is not None:
        payload['oauth_token'] = oauth_token
    if expires is not None and (isinstance(expires, datetime) or isinstance(expires, int)):
        value = expires
        if isinstance(expires, datetime):
            value = int(time.mktime(expires.timetuple()))
        payload['expires'] = value
    if app_data is not None and isinstance(app_data, dict):
        payload['app_data'] = app_data
    if page is not None and isinstance(page, dict):
        payload['page'] = page

    return _create_signed_request_parameter(app_secret, json.dumps(payload))

def _prepend_signature(app_secret, payload):
        """
            Returns a SHA256 signed and base64 encoded signature based on the given payload

            Arguments:
            app_secret -- the secret key that Facebook assigns to each Facebook application
            payload -- a base64url encoded String
        """
        dig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()
        dig = base64.urlsafe_b64encode(dig)
        return dig

def _create_signed_request_parameter(app_secret, payload):
        """
            Returns a String value usable as the Facebook signed_request parameter. The String will be based on the given payload.
            The signed_request parameter is the concatenation of a HMAC SHA-256 signature string, a period (.), and a
            the base64url encoded payload.

            Arguments:
            app_secret -- the secret key that Facebook assigns to each Facebook application
            payload -- a JSON formatted String
        """
        base64_encoded_payload = base64.urlsafe_b64encode(payload)
        return _prepend_signature(app_secret, base64_encoded_payload) + "." + base64_encoded_payload

# ---------------------------------------------------------------------
# End snatched code by Reik Schatz.
# ---------------------------------------------------------------------