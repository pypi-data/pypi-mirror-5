import json
from unittest import TestCase

from requests.exceptions import ConnectionError, Timeout
from mock import Mock, patch

from basket import (BasketException, confirm, debug_user, get_newsletters,
                    request, subscribe, unsubscribe, update_user, user)
from basket.base import basket_url, parse_response


# Warning: there are two request() methods, one in basket-client and
# one in the requests library. Pay attention, it's very confusing.

class TestBasketClient(TestCase):

    def test_basket_url_no_token(self):
        """Form basket URL properly when no token used"""
        with patch('basket.base.BASKET_URL', new="BASKET_URL"):
            result = basket_url("METHOD")
        self.assertEqual("BASKET_URL/news/METHOD/", result)

    def test_basket_url_with_token(self):
        """Form basket URL properly when token used"""
        with patch('basket.base.BASKET_URL', new="BASKET_URL"):
            result = basket_url("METHOD", "TOKEN")
        self.assertEqual("BASKET_URL/news/METHOD/TOKEN/", result)

    def test_response_not_200(self):
        """parse_response() raises exception on non-200 status code"""
        # and puts the status code on the exception
        res = Mock(status_code=666)
        try:
            parse_response(res)
        except BasketException as e:
            self.assertEqual(666, e.status_code)
        else:
            self.fail("parse_response should have raised BasketException")

    def test_response_error(self):
        """parse_response() raises exception on status=error"""
        content = json.dumps({'status': 'error', 'desc': 'ERROR'})
        res = Mock(status_code=200, content=content)
        with self.assertRaises(BasketException):
            parse_response(res)

    def test_response_content(self):
        """parse_response() returns parsed response content if no error"""
        data = {u'status': u'ok', u'foo': u'bar'}
        content = json.dumps(data)
        res = Mock(status_code=200, content=content)
        result = parse_response(res)
        self.assertEqual(data, result)

    def test_request(self):
        """
        request() calls requests.request() with the expected parms
        if everything is normal, and returns the expected result.
        """
        response_data = {u'status': u'ok', u'foo': u'bar'}
        action, method, token = "ACTION", "METHOD", "TOKEN"
        url = basket_url(action, token)
        with patch('basket.base.requests.request', autospec=True) \
                as request_call:
            request_call.return_value = Mock(status_code=200,
                                             content=json.dumps(response_data))
            result = request(method, action, data="DATA",
                             token=token, params="PARAMS")

        request_call.assert_called_with(method, url, data="DATA",
                                        params="PARAMS", timeout=10)
        self.assertEqual(response_data, result)

    def test_request_newsletters_string(self):
        """
        If request is passed newsletters as a string, newsletters is passed
        along unaltered.
        """
        input_data = {'newsletters': 'one,two'}
        action, method, token = "ACTION", "METHOD", "TOKEN"
        url = basket_url(action, token)
        content = {'one': 100, 'two': 200}
        with patch('basket.base.requests.request', autospec=True) \
                as request_call:
            request_call.return_value = Mock(status_code=200,
                                             content=json.dumps(content))
            result = request(method, action, data=input_data,
                             token=token, params="PARAMS")

        request_call.assert_called_with(method, url, data=input_data,
                                        params="PARAMS", timeout=10)
        self.assertEqual(content, result)

    def test_request_newsletters_non_string(self):
        """
        If request is passed newsletters as a non-string, newsletters is
        converted to a comma-separated string
        """
        response_data = {u'status': u'ok', u'foo': u'bar'}
        input_data = {'newsletters': ['one', 'two'], 'thing': 1}
        expected_input_data = input_data.copy()
        newsletters = ','.join(input_data['newsletters'])
        expected_input_data['newsletters'] = newsletters
        action, method, token = "ACTION", "METHOD", "TOKEN"
        url = basket_url(action, token)
        with patch('basket.base.requests.request', autospec=True) \
                as request_call:
            request_call.return_value = Mock(status_code=200,
                                             content=json.dumps(response_data))
            result = request(method, action, data=input_data,
                             token=token, params="PARAMS")

        request_call.assert_called_with(method, url, data=expected_input_data,
                                        params="PARAMS", timeout=10)
        self.assertEqual(response_data, result)

    def test_request_conn_error(self):
        """
        If requests throws a ConnectionError, it's converted to
        a BasketException
        """
        input_data = {'newsletters': ['one', 'two'], 'thing': 1}
        expected_input_data = input_data.copy()
        newsletters = ','.join(input_data['newsletters'])
        expected_input_data['newsletters'] = newsletters
        action, method, token = "ACTION", "METHOD", "TOKEN"
        with patch('basket.base.requests.request', autospec=True) \
                as request_call:
            request_call.side_effect = ConnectionError
            with self.assertRaises(BasketException):
                request(method, action, data=input_data,
                        token=token, params="PARAMS")

    def test_request_timeout(self):
        """
        If requests times out, it's converted to
        a BasketException
        """
        input_data = {'newsletters': ['one', 'two'], 'thing': 1}
        expected_input_data = input_data.copy()
        newsletters = ','.join(input_data['newsletters'])
        expected_input_data['newsletters'] = newsletters
        action, method, token = "ACTION", "METHOD", "TOKEN"
        with patch('basket.base.requests.request', autospec=True) \
                as request_call:
            request_call.side_effect = Timeout
            with self.assertRaises(BasketException):
                request(method, action, data=input_data,
                        token=token, params="PARAMS")

    def test_subscribe(self):
        """
        subscribe calls request with the expected parms and returns the result
        """
        email = "user1@example.com"
        newsletters = ['news1', 'news2']
        kwargs = {
            'arg1': 100,
            'arg2': 200,
        }
        expected_kwargs = kwargs.copy()
        expected_kwargs['email'] = email
        expected_kwargs['newsletters'] = newsletters
        with patch('basket.base.request', autospec=True) as request_call:
            result = subscribe(email, newsletters, **kwargs)

        request_call.assert_called_with('post', 'subscribe',
                                        data=expected_kwargs)
        self.assertEqual(request_call.return_value, result)

    def test_unsubscribe(self):
        """
        unsubscribe calls request with the expected parms, returns the result
        """
        email = "user1@example.com"
        newsletters = ['news1', 'news2']
        token = "TOKEN"
        optout = False
        expected_data = {
            'email': email,
            'newsletters': newsletters,
        }
        with patch('basket.base.request', autospec=True) as request_call:
            result = unsubscribe(token, email, newsletters, optout)

        request_call.assert_called_with('post', 'unsubscribe',
                                        data=expected_data,
                                        token=token)
        self.assertEqual(request_call.return_value, result)

    def test_unsubscribe_optout(self):
        """
        unsubscribe calls request with the expected parms and returns the
        result. optout is passed if true, instead of newsletters.
        """
        email = "user1@example.com"
        newsletters = ['news1', 'news2']
        token = "TOKEN"
        optout = True
        expected_data = {
            'email': email,
            'optout': 'Y'
        }
        with patch('basket.base.request', autospec=True) as request_call:
            result = unsubscribe(token, email, newsletters, optout)

        request_call.assert_called_with('post', 'unsubscribe',
                                        data=expected_data,
                                        token=token)
        self.assertEqual(request_call.return_value, result)

    def test_unsubscribe_bad_args(self):
        """
        unsubscribe must be passed newsletters or optout, or it raises
        BasketException
        """
        email = "user1@example.com"
        newsletters = None
        token = "TOKEN"
        optout = None
        with patch('basket.base.request', autospec=True):
            with self.assertRaises(BasketException):
                unsubscribe(token, email, newsletters, optout)

    def test_user(self):
        """
        user passes the expected args to request() and returns the result.
        """
        token = "TOKEN"
        with patch('basket.base.request', autospec=True) as request_call:
            result = user(token)
        request_call.assert_called_with('get', 'user', token=token)
        self.assertEqual(request_call.return_value, result)

    def test_update_user(self):
        """
        update_user passes the expected args to request(), returns the result.
        """
        token = "TOKEN"
        kwargs = {
            'one': 100,
            'two': 200,
        }
        with patch('basket.base.request', autospec=True) as request_call:
            result = update_user(token, **kwargs)
        request_call.assert_called_with('post', 'user', data=kwargs,
                                        token=token)
        self.assertEqual(request_call.return_value, result)

    def test_debug_user(self):
        """
        debug_user passes the expected args to request(), returns the result.
        """
        email = "user@example.com"
        supertoken = "STOKEN"
        params = {'email': email, 'supertoken': supertoken}
        with patch('basket.base.request', autospec=True) as request_call:
            result = debug_user(email, supertoken)
        request_call.assert_called_with('get', 'debug-user', params=params)
        self.assertEqual(request_call.return_value, result)

    def test_get_newsletters(self):
        """
        get_newsletters passes the expected args to request() and returns
        the 'newsletters' part of what it returns
        """
        with patch('basket.base.request', autospec=True) as request_call:
            request_call.return_value = {'newsletters': 'FOO BAR'}
            result = get_newsletters()
        request_call.assert_called_with('get', 'newsletters')
        self.assertEqual('FOO BAR', result)

    def test_confirm(self):
        """
        confirm() passes the expected args to request, and returns the result.
        """
        token = "TOKEN"
        with patch('basket.base.request', autospec=True) as request_call:
            result = confirm(token)
        request_call.assert_called_with('post', 'confirm', token=token)
        self.assertEqual(request_call.return_value, result)
