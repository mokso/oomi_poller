import unittest
from unittest.mock import patch, Mock
from datetime import datetime, timezone
from oomi import OomiClient

class TestOomiClient(unittest.TestCase):

    @patch('oomi.requests.Session')
    def setUp(self, MockSession):
        self.mock_session = MockSession.return_value
        self.client = OomiClient('test_user', 'test_password')

    def test_login_success(self):
        # Mock the responses for the login process
        self.mock_session.get.return_value.text = '<input name="__RequestVerificationToken" type="hidden" value="test_token" />'
        self.mock_session.post.return_value.status_code = 200

        self.client.login()

        self.assertEqual(self.client.verificationtoken, 'test_token')
        self.mock_session.get.assert_called_once_with('https://online.oomi.fi/eServices/Online/IndexNoAuth')
        self.mock_session.post.assert_called_once_with(
            'https://online.oomi.fi/eServices/Online/Login',
            data={
                "UserName": 'test_user',
                "Password": 'test_password',
                "__RequestVerificationToken": 'test_token',
            }
        )

    def test_login_failure_no_token(self):
        self.mock_session.get.return_value.text = ''
        with self.assertRaises(ValueError):
            self.client.login()

    def test_login_failure_wrong_credentials(self):
        self.mock_session.get.return_value.text = '<input name="__RequestVerificationToken" type="hidden" value="test_token" />'
        self.mock_session.post.return_value.status_code = 401

        with self.assertRaises(ValueError):
            self.client.login()

    def test_get_consumption_data(self):
        self.client.verificationtoken = 'test_token'
        self.mock_session.get.return_value.status_code = 200
        self.mock_session.get.return_value.text = 'var model = {"Data":[[1682985600000,10.0],[1682989200000,20.0]]};'
        data = self.client.get_consumption_data('test_meteringpoint')

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0], datetime(2023, 5, 1, 21, 0, tzinfo=timezone.utc))        
        self.assertEqual(data[0][1], 10.0)        
        self.assertEqual(data[0][0], datetime(2023, 5, 1, 22, 0, tzinfo=timezone.utc))   
        self.assertEqual(data[1][1], 20.0)


    def test_get_consumption_data_not_logged_in(self):
        with self.assertRaises(ValueError):
            self.client.get_consumption_data('test_meteringpoint')

    def test_get_consumption_data_no_data(self):
        self.client.verificationtoken = 'test_token'
        self.mock_session.get.return_value.text = 'var model = {};'

        with self.assertRaises(ValueError):
            self.client.get_consumption_data('test_meteringpoint')

if __name__ == '__main__':
    unittest.main()