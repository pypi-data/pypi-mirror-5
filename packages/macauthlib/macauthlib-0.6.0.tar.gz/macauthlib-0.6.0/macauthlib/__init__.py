# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
"""

A library for implementing the MAC Access Authentication protocol:

    http://tools.ietf.org/html/draft-ietf-oauth-v2-http-mac-01

Typical use for a client program would be to sign a request object like
this::

    macauthlib.sign_request(request, id, key)

Typical use for a server program would be to verify a signed request like
this::

    id = macauthlib.get_id(request)
    if id not None:
        key = somehow_lookup_the_mac_key(id)
        if macauthlib.check_signature(request, key):
            return True
    return False

"""

__ver_major__ = 0
__ver_minor__ = 6
__ver_patch__ = 0
__ver_sub__ = ""
__ver_tuple__ = (__ver_major__, __ver_minor__, __ver_patch__, __ver_sub__)
__version__ = "%d.%d.%d%s" % __ver_tuple__


import os
import time
import hmac
from hashlib import sha1

from macauthlib import utils
from macauthlib.noncecache import NonceCache


# Global NonceCache instance used when a specific cache is not specified.
DEFAULT_NONCE_CACHE = None


@utils.normalize_request_object
def sign_request(request, id, key, hashmod=None, params=None):
    """Sign the given request using MAC access authentication.

    This function implements the client-side request signing algorithm as
    expected by the server, i.e. MAC access authentication as defined by
    RFC-TODO.  It takes a WebOb Request object and inserts the appropriate
    signature into its Authorization header.
    """
    # Use explicitly-given parameters, or those from the request.
    if params is None:
        params = utils.parse_authz_header(request, {})
        if params and params.pop("scheme") != "MAC":
            params.clear()
    # Give sensible values to any parameters that weren't specified.
    params["id"] = id
    if "ts" not in params:
        params["ts"] = str(int(time.time()))
    if "nonce" not in params:
        params["nonce"] = utils.b64encode(os.urandom(5))
    # Calculate the signature and add it to the parameters.
    params["mac"] = get_signature(request, key, hashmod, params)
    # Serialize the parameters back into the authz header, and return it.
    # WebOb has logic to do this that's not perfect, but good enough for us.
    request.authorization = ("MAC", params)
    return request.headers["Authorization"]


@utils.normalize_request_object
def get_id(request, params=None):
    """Get the MAC id from the given request.

    This function extracts the claimed MAC id from the authorization header of
    the given request.  It does not verify the signature, since that would
    require looking up the corresponding MAC secret key.
    """
    if params is None:
        params = utils.parse_authz_header(request, {})
    if params.get("scheme") != "MAC":
        return None
    return params.get("id", None)


@utils.normalize_request_object
def get_signature(request, key, hashmod=None, params=None):
    """Get the MAC signature for the given request.

    This function calculates the MAC signature for the given request and
    returns it as a string.

    If the "params" parameter is not None, it is assumed to be a pre-parsed
    dict of MAC parameters as one might find in the Authorization header.  If
    it is missing or None then the Authorization header from the request will
    be parsed to determine the necessary parameters.
    """
    if params is None:
        params = utils.parse_authz_header(request, {})
    if hashmod is None:
        hashmod = sha1
    sigstr = utils.get_normalized_request_string(request, params)
    # The spec mandates that ids and keys must be ascii.
    # It's therefore safe to encode like this before doing the signature.
    sigstr = sigstr.encode("ascii")
    key = key.encode("ascii")
    return utils.b64encode(hmac.new(key, sigstr, hashmod).digest())


@utils.normalize_request_object
def check_signature(request, key, hashmod=None, params=None, nonces=None):
    """Check that the request is correctly signed with the given MAC key.

    This function checks the MAC signature in the given request against its
    expected value, returning True if they match and false otherwise.

    If the "params" parameter is not None, it is assumed to be a pre-parsed
    dict of MAC parameters as one might find in the Authorization header.  If
    it is missing or  None then the Authorization header from the request will
    be parsed to determine the necessary parameters.

    If the "nonces" parameter is not None, it must be a NonceCache object
    used to check validity of the signature nonce.  If not specified then a
    default global cache will be used.  To disable nonce checking (e.g. during
    testing) pass nonces=False.
    """
    global DEFAULT_NONCE_CACHE
    if nonces is None:
        nonces = DEFAULT_NONCE_CACHE
        if nonces is None:
            nonces = DEFAULT_NONCE_CACHE = NonceCache()
    if params is None:
        params = utils.parse_authz_header(request, {})
    if params.get("scheme") != "MAC":
        return False
    # Any KeyError here indicates a missing parameter.
    # Any ValueError here indicates an invalid parameter.
    try:
        id = params["id"]
        timestamp = int(params["ts"])
        nonce = params["nonce"]
        # Check validity of the signature.
        expected_sig = get_signature(request, key, hashmod, params)
        if utils.strings_differ(params["mac"], expected_sig):
            return False
        # Check freshness of the nonce.
        # This caches it so future use of the nonce will fail.
        # We do this *after* successul sig check to avoid DOS attacks.
        if nonces is not False:
            if not nonces.check_nonce(id, timestamp, nonce):
                return False
    except (KeyError, ValueError):
        return False
    return True
