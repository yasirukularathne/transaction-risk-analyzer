import unittest
from unittest.mock import patch, MagicMock
import json
import os
from Server import call_groq_api, build_optimized_groq_prompt


class TestGroqApiConnection(unittest.TestCase):

    @patch('Server.GROQ_API_KEY', 'dummy_api_key')
    @patch('Server.requests.post')
    def test_api_connection_attempt(self, mock_post):
        """Test that the function attempts to connect to the Groq API with correct parameters"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"risk_score": 0.2, "risk_factors": ["test"], "reasoning": "test", "recommended_action": "allow"}'
                }
            }]
        }
        mock_post.return_value = mock_response

        # Sample transaction data
        transaction_data = {
            "transaction_id": "tx_123",
            "timestamp": "2025-06-24T10:00:00Z",
            "amount": 100.00,
            "currency": "USD",
            "customer": {
                "id": "cust_123",
                "country": "US",
                "ip_address": "192.168.1.1"
            },
            "payment_method": {
                "type": "credit_card",
                "last_four": "1234",
                "country_of_issue": "US"
            },
            "merchant": {
                "id": "merch_123",
                "name": "Test Merchant",
                "category": "retail"
            }
        }

        # Call the function
        result = call_groq_api(transaction_data)        # Check if requests.post was called with the correct URL
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        # Verify the URL is correct (URL is the first positional argument)
        self.assertEqual(call_args[0][0], 'https://api.groq.com/openai/v1/chat/completions')
        
        # Verify headers contain authorization with API key
        self.assertEqual(call_args[1]['headers']['Authorization'], 'Bearer dummy_api_key')
        self.assertEqual(call_args[1]['headers']['Content-Type'], 'application/json')
          # Verify the expected prompt was used
        expected_prompt = build_optimized_groq_prompt(transaction_data)
        actual_prompt = json.loads(call_args[1]['data'])
        self.assertEqual(actual_prompt, expected_prompt)
        
        # Verify timeout parameter
        self.assertEqual(call_args[1].get('timeout', None), 30)

    @patch('Server.GROQ_API_KEY', '')
    @patch('Server.requests.post')
    def test_missing_api_key(self, mock_post):
        """Test the behavior when GROQ API key is not configured"""
        transaction_data = {
            "transaction_id": "tx_123",
            "timestamp": "2025-06-24T10:00:00Z",
            "amount": 100.00,
            "currency": "USD", 
            "customer": {
                "id": "cust_123",
                "country": "US",
                "ip_address": "192.168.1.1"
            },
            "payment_method": {
                "type": "credit_card",
                "last_four": "1234",
                "country_of_issue": "US"
            },
            "merchant": {
                "id": "merch_123",
                "name": "Test Merchant", 
                "category": "retail"
            }
        }
        
        # Call the function
        result = call_groq_api(transaction_data)
        
        # Verify API was not called
        mock_post.assert_not_called()
        
        # Verify default response with error message
        self.assertEqual(result["risk_score"], 0.5)
        self.assertEqual(result["risk_factors"], ["API configuration error"])
        self.assertEqual(result["reasoning"], "GROQ API key not configured")
        self.assertEqual(result["recommended_action"], "review")


if __name__ == '__main__':
    unittest.main()
