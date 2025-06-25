import unittest
import json
import base64
from flask import Flask, jsonify, request
from functools import wraps
from Server import require_basic_auth

class AuthenticationReceiveTest(unittest.TestCase):
    """Test suite to verify if the authentication credentials are properly received"""
    
    def setUp(self):
        """Set up test Flask app with a route that checks received credentials"""
        self.app = Flask(__name__)
        self.received_username = None
        self.received_password = None
        
        # Create a custom decorator that captures the received credentials
        def test_auth_capture(username, password):
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    auth_header = request.headers.get('Authorization')
                    if auth_header and auth_header.startswith('Basic '):
                        try:
                            encoded_credentials = auth_header.split(' ')[1]
                            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                            self.received_username, self.received_password = decoded_credentials.split(':')
                        except Exception:
                            pass
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
        
        # Create a route with both our test decorator and the actual auth decorator
        @self.app.route('/auth-check')
        @test_auth_capture('test_user', 'test_pass')  # This captures credentials
        @require_basic_auth('admin', 'secret123')     # This performs actual auth
        def protected_endpoint():
            return jsonify({'message': 'Access granted'})
        
        self.client = self.app.test_client()
    
    def test_auth_credentials_received(self):
        """Test specifically if authentication credentials are correctly received"""
        # Reset captured values
        self.received_username = None
        self.received_password = None
        
        # Send request with specific credentials
        credentials = base64.b64encode(b'admin:secret123').decode('utf-8')
        response = self.client.get(
            '/auth-check', 
            headers={'Authorization': f'Basic {credentials}'}
        )
        
        # Verify credentials were received correctly
        self.assertEqual(self.received_username, 'admin')
        self.assertEqual(self.received_password, 'secret123')
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_credentials_format(self):
        """Test credentials with invalid format"""
        # Reset captured values
        self.received_username = None
        self.received_password = None
        
        # Send malformed credentials (missing colon)
        malformed_credentials = base64.b64encode(b'adminNoPassword').decode('utf-8')
        response = self.client.get(
            '/auth-check',
            headers={'Authorization': f'Basic {malformed_credentials}'}
        )
        
        # The credentials should not be parsed successfully
        self.assertIsNone(self.received_username)
        self.assertIsNone(self.received_password)
        self.assertEqual(response.status_code, 401)
    
    def test_wrong_auth_scheme(self):
        """Test using wrong authentication scheme"""
        # Reset captured values
        self.received_username = None
        self.received_password = None
        
        # Send Bearer token instead of Basic Auth
        credentials = base64.b64encode(b'admin:secret123').decode('utf-8')
        response = self.client.get(
            '/auth-check',
            headers={'Authorization': f'Bearer {credentials}'}
        )
        
        # Auth header shouldn't be processed as Basic
        self.assertIsNone(self.received_username)
        self.assertIsNone(self.received_password)
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
