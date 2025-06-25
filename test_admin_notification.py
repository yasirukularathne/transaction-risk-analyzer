import unittest
from unittest.mock import patch, MagicMock
from Server import send_admin_notification, NOTIFICATIONS

class TestAdminNotification(unittest.TestCase):
    """Simple unittest for testing the admin notification system"""
    
    def setUp(self):
        """Clear notifications before each test"""
        # Clear the global NOTIFICATIONS list
        NOTIFICATIONS.clear()
    
    def test_high_risk_transaction_flagged(self):
        """Test that high-risk transactions trigger notifications"""
        # Sample transaction data
        transaction = {
            "transaction_id": "tx_high_risk_123",
            "timestamp": "2025-06-24T12:00:00Z",
            "amount": 5000.00,
            "currency": "USD",
            "customer": {
                "id": "cust_123",
                "country": "US",
                "ip_address": "192.168.1.1"
            },
            "payment_method": {
                "type": "credit_card",
                "last_four": "9999",
                "country_of_issue": "RU"
            },
            "merchant": {
                "id": "merch_123",
                "name": "Test Merchant",
                "category": "electronics"
            }
        }
        
        # Risk analysis with high risk score (>= 0.7)
        risk_analysis = {
            "risk_score": 0.85,
            "risk_factors": ["High-risk country", "Large transaction amount"],
            "reasoning": "Transaction from high-risk country with large amount",
            "recommended_action": "block"
        }
        
        # Mock the socketio.emit function
        with patch('Server.socketio.emit') as mock_emit:
            # Call the notification function
            notification = send_admin_notification(transaction, risk_analysis)
            
            # Verify a notification was created
            self.assertIsNotNone(notification)
            
            # Verify the notification was added to the global list
            self.assertEqual(len(NOTIFICATIONS), 1)
            
            # Verify notification has correct data
            self.assertEqual(NOTIFICATIONS[0]['transaction_id'], "tx_high_risk_123")
            self.assertEqual(NOTIFICATIONS[0]['risk_analysis']['risk_score'], 0.85)
            self.assertEqual(NOTIFICATIONS[0]['risk_analysis']['recommended_action'], "block")
            
            # Verify socketio.emit was called with correct event
            mock_emit.assert_called_once()
            self.assertEqual(mock_emit.call_args[0][0], 'new_transaction')
    
    def test_low_risk_transaction_not_flagged(self):
        """Test that low-risk transactions don't trigger notifications"""
        # Sample transaction data
        transaction = {
            "transaction_id": "tx_low_risk_456",
            "timestamp": "2025-06-24T12:00:00Z",
            "amount": 50.00,
            "currency": "USD",
            "customer": {
                "id": "cust_456",
                "country": "US",
                "ip_address": "192.168.1.2"
            },
            "payment_method": {
                "type": "credit_card",
                "last_four": "1234",
                "country_of_issue": "US"
            },
            "merchant": {
                "id": "merch_456",
                "name": "Test Merchant",
                "category": "retail"
            }
        }
        
        # Risk analysis with low risk score (< 0.7)
        risk_analysis = {
            "risk_score": 0.2,
            "risk_factors": ["None"],
            "reasoning": "Normal transaction pattern",
            "recommended_action": "allow"
        }
        
        # Mock the socketio.emit function
        with patch('Server.socketio.emit') as mock_emit:
            # Call the notification function
            notification = send_admin_notification(transaction, risk_analysis)
            
            # Verify no notification was created
            self.assertIsNone(notification)
            
            # Verify no notification was added to the global list
            self.assertEqual(len(NOTIFICATIONS), 0)
            
            # Verify socketio.emit was not called
            mock_emit.assert_not_called()

if __name__ == '__main__':
    unittest.main()
