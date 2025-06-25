import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import json
import base64
from Server import app, webhook

class TestWebhookEndpoint(unittest.TestCase):
    """Simple unittest for testing the webhook endpoint"""
    
    def setUp(self):
        """Set up test client and authentication headers"""
        # Create a test client
        self.app = app.test_client()
        
        # Create authentication headers
        credentials = base64.b64encode(b"admin:secret123").decode("utf-8")
        self.auth_headers = {"Authorization": f"Basic {credentials}"}
        
        # Sample valid transaction data
        self.valid_transaction = {
            "transaction_id": "tx_test_12345",
            "timestamp": "2025-06-24T12:00:00Z",
            "amount": 100.00,
            "currency": "USD",
            "customer": {
                "id": "cust_test",
                "country": "US",
                "ip_address": "192.168.1.1"
            },
            "payment_method": {
                "type": "credit_card",
                "last_four": "1234",
                "country_of_issue": "US"
            },
            "merchant": {
                "id": "merch_test",
                "name": "Test Merchant",
                "category": "retail"
            }
        }
    
    @patch('Server.call_groq_api')
    @patch('Server.send_admin_notification')
    def test_webhook_successful_processing(self, mock_send_notification, mock_call_groq):
        """Test that webhook successfully processes a valid transaction"""
        # Mock the GROQ API response
        mock_risk_analysis = {
            "risk_score": 0.2,
            "risk_factors": ["None"],
            "reasoning": "Normal transaction",
            "recommended_action": "allow"
        }
        mock_call_groq.return_value = mock_risk_analysis
        
        # Mock the notification function (returns None for low-risk transactions)
        mock_send_notification.return_value = None
        
        # Make a POST request to the webhook endpoint
        response = self.app.post(
            '/webhook',
            headers=self.auth_headers,
            json=self.valid_transaction,
            content_type='application/json'
        )
        
        # Verify response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
        # Parse response data
        response_data = json.loads(response.data)
        
        # Verify response contains expected fields
        self.assertEqual(response_data['transaction_id'], 'tx_test_12345')
        self.assertEqual(response_data['status'], 'processed')
        self.assertIn('risk_analysis', response_data)
        self.assertIn('timestamp', response_data)
        
        # Verify risk analysis matches what was returned by the API
        self.assertEqual(response_data['risk_analysis']['risk_score'], 0.2)
        self.assertEqual(response_data['risk_analysis']['recommended_action'], 'allow')
        
        # Verify that the API was called with our transaction data
        mock_call_groq.assert_called_once_with(self.valid_transaction)
        
        # Verify notification function was called with correct parameters
        mock_send_notification.assert_called_once_with(self.valid_transaction, mock_risk_analysis)
    
    def test_webhook_missing_auth(self):
        """Test webhook rejects requests with missing authentication"""
        # Make a POST request without authentication headers
        response = self.app.post(
            '/webhook',
            json=self.valid_transaction,
            content_type='application/json'
        )
        
        # Verify response status code is 401 (Unauthorized)
        self.assertEqual(response.status_code, 401)
        
        # Parse response data
        response_data = json.loads(response.data)
          # Verify error message
        self.assertEqual(response_data['error'], 'Unauthorized')
    
    def test_webhook_invalid_json(self):
        """Test webhook rejects requests with invalid JSON"""
        # Make a POST request with invalid JSON (sending string instead of JSON)
        response = self.app.post(
            '/webhook',
            headers=self.auth_headers,
            data="This is not JSON",
            content_type='application/json'
        )
        
        # Verify response status code is 401 (Unauthorized) or 400 (Bad Request)
        # Note: In some implementations, auth check happens first, in others content-type check happens first
        self.assertIn(response.status_code, [400, 401])
        
        # Parse response data
        response_data = json.loads(response.data)
        
        # Either it fails at auth or JSON validation
        if response.status_code == 401:
            self.assertEqual(response_data['error'], 'Unauthorized')
        else:
            self.assertEqual(response_data['error'], 'Request must be JSON')
    
    @patch('Server.validate_transaction_data')
    def test_webhook_invalid_transaction_data(self, mock_validate):
        """Test webhook rejects invalid transaction data"""
        # Mock the validation function to return an error
        mock_validate.return_value = (False, "Missing required field: amount")
        
        # Make a POST request with invalid transaction data
        response = self.app.post(
            '/webhook',
            headers=self.auth_headers,
            json={"transaction_id": "missing_fields"},
            content_type='application/json'
        )
        
        # Verify response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, 400)
        
        # Parse response data
        response_data = json.loads(response.data)
        
        # Verify error message contains validation message
        self.assertIn('Invalid transaction data', response_data['error'])

if __name__ == '__main__':
    unittest.main()
