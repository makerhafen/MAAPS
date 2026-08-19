# Test for client/hardware.py - Hardware Daemon
# This uses Bottle's built-in test client against the dummy mode

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'client'))

import bottle
from bottle import Bottle, Response, Request


class TestHardwareDaemon(unittest.TestCase):
    """Tests for client/hardware.py using Bottle test client in dummy mode."""

    def setUp(self):
        import importlib.util
        hardware_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'client', 'hardware.py'
        )
        spec = importlib.util.spec_from_file_location("hardware", hardware_path)
        hardware = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hardware)
        # Initialize the global objects that the routes depend on
        hardware.rfid = hardware.RFID()
        hardware.relayboard = hardware.RelayBoard()
        # Use the default bottle app
        self.app = bottle.default_app()

    def tearDown(self):
        # Clean up the default app routes for next test
        bottle.default_app().reset()

    def test_hardware_daemon_imports(self):
        """Test that hardware.py can be imported and dummy mode works."""
        self.assertIsInstance(self.app, Bottle)

    def _request(self, path, method='GET'):
        """Make a test request to the bottle app."""
        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'PATH_INFO': path,
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '8080',
            'wsgi.url_scheme': 'http',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
            'CONTENT_LENGTH': '0',
            'wsgi.errors': sys.stderr,
        }
        
        # Capture response
        response_data = {}
        def start_response(status, headers, exc_info=None):
            response_data['status'] = status
            response_data['headers'] = headers
        
        # Call the WSGI app
        body = self.app(environ, start_response)
        response_body = b''.join(body).decode()
        
        # Parse status
        status_code = int(response_data['status'].split()[0])
        
        return type('Response', (), {
            'status': status_code,
            'body': response_body,
        })()

    def test_rfid_read_dummy(self):
        """Test /rfid/read/ endpoint in dummy mode."""
        response = self._request('/rfid/read/')
        self.assertEqual(response.status, 200)
        data = response.body.strip().split('\t')
        self.assertEqual(len(data), 2)
        # Should return dummy token in format: <token_id>\t<text>

    def test_rfid_write_dummy(self):
        """Test /rfid/write/<value> endpoint in dummy mode."""
        test_token = "U:testuser;testuuid123"
        response = self._request(f'/rfid/write/{test_token}')
        self.assertEqual(response.status, 200)
        self.assertIn("ok", response.body.lower())

    def test_relay_control_dummy(self):
        """Test /relay/<names>/<value> endpoint in dummy mode."""
        response = self._request('/relay/all/on')
        self.assertEqual(response.status, 200)
        self.assertIn("ok", response.body.lower())

        response = self._request('/relay/1/off')
        self.assertEqual(response.status, 200)
        self.assertIn("ok", response.body.lower())


if __name__ == '__main__':
    unittest.main()
