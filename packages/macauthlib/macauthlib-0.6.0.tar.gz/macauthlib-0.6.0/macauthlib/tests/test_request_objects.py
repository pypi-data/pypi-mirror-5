# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import unittest

if sys.version_info > (3,):  # pragma: nocover
    from io import BytesIO
else:  # pragma: nocover
    from StringIO import StringIO as BytesIO  # NOQA

import webob
import requests
import requests.auth

from macauthlib import sign_request, check_signature

# These parameters define a known-good signature for a specific request.
# We test a bunch of different ways to input that request into the lib
# and check whether they all agree on the signature.

TEST_REQ = b"POST /resource/1?b=1&a=2 HTTP/1.1\r\n"\
           b"Host: example.com\r\n"\
           b"Content-Length: 11\r\n"\
           b"\r\n"\
           b"hello world"

TEST_REQ_SIGNED = b"POST /resource/1?b=1&a=2 HTTP/1.1\r\n"\
                  b"Host: example.com\r\n"\
                  b"Content-Length: 11\r\n"\
                  b"Authorization: MAC nonce=\"dj83hs9s\","\
                  b"                   mac=\"SIBz/j9mI1Ba2Y+10wdwbQGv2Yk=\","\
                  b"                   id=\"h480djs93hd8\","\
                  b"                   ts=\"1336363200\"\r\n"\
                  b"\r\n"\
                  b"hello world"

TEST_PARAMS = {
    "id": "h480djs93hd8",
    "ts": "1336363200",
    "nonce": "dj83hs9s"
}

TEST_ID = "h480djs93hd8"

TEST_KEY = "489dks293j39"

TEST_SIG = "SIBz/j9mI1Ba2Y+10wdwbQGv2Yk="


class TestRequestObjects(unittest.TestCase):

    def test_passing_webob_request_as_request_object(self):
        req = webob.Request.from_bytes(TEST_REQ)
        assert not check_signature(req, TEST_KEY, nonces=False)
        authz = sign_request(req, TEST_ID, TEST_KEY, params=TEST_PARAMS)
        assert TEST_SIG in authz
        assert check_signature(req, TEST_KEY, nonces=False)

    def test_passing_environ_dict_as_request_object(self):
        req = {
            "wsgi.url_scheme": "http",
            "REQUEST_METHOD": "POST",
            "HTTP_HOST": "example.com",
            "HTTP_CONTENT_LENGTH": "11",
            "PATH_INFO": "/resource/1",
            "QUERY_STRING": "b=1&a=2",
            "wsgi.input": BytesIO(b"hello world")
        }
        assert not check_signature(req, TEST_KEY, nonces=False)
        authz = sign_request(req, TEST_ID, TEST_KEY, params=TEST_PARAMS)
        assert TEST_SIG in authz
        assert check_signature(req, TEST_KEY, nonces=False)

    def test_passing_bytestring_as_request_object(self):
        assert not check_signature(TEST_REQ, TEST_KEY, nonces=False)
        authz = sign_request(TEST_REQ, TEST_ID, TEST_KEY, params=TEST_PARAMS)
        assert TEST_SIG in authz
        assert check_signature(TEST_REQ_SIGNED, TEST_KEY, nonces=False)

    def test_passing_filelike_as_request_object(self):
        req = BytesIO(TEST_REQ)
        assert not check_signature(req, TEST_KEY, nonces=False)
        req = BytesIO(TEST_REQ)
        authz = sign_request(req, TEST_ID, TEST_KEY, params=TEST_PARAMS)
        assert TEST_SIG in authz
        req = BytesIO(TEST_REQ_SIGNED)
        assert check_signature(req, TEST_KEY, nonces=False)

    def test_passing_requests_request_as_request_object(self):
        req = requests.Request(
            url="http://example.com/resource/1",
            method="POST",
            params=[("b", "1"), ("a", "2")],
            data="hello world",
        )
        req = req.prepare()
        assert not check_signature(req, TEST_KEY, nonces=False)
        authz = sign_request(req, TEST_ID, TEST_KEY, params=TEST_PARAMS)
        assert TEST_SIG in req.headers['Authorization']
        assert check_signature(req, TEST_KEY, nonces=False)

    def test_using_sign_request_in_a_requests_auth_object(self):
        # We don't actually want to perform the request, so
        # we have the auth handler error out once it has run 
        # and we catch-and-ignore that error.
        class HTTPMacAuth(requests.auth.AuthBase):
            def __call__(self, req):
                sign_request(req, TEST_ID, TEST_KEY, params=TEST_PARAMS)
                assert check_signature(req, TEST_KEY, nonces=False)
                assert TEST_SIG in req.headers['Authorization']
                raise RuntimeError("aborting the request")

        try:
            requests.post("http://example.com/resource/1",
                         params=[("b", "1"), ("a", "2")],
                         data="hello world",
                         auth=HTTPMacAuth())
        except RuntimeError as e:
            assert "aborting the request" in str(e)
