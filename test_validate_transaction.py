import pytest
from Server import validate_transaction_data

# Valid transaction fixture for testing
@pytest.fixture
def valid_transaction():
    return {
        "transaction_id": "tx_12345",
        "timestamp": "2023-04-01T12:00:00Z",
        "amount": 100.00,
        "currency": "USD",
        "customer": {
            "id": "cust_123",
            "country": "US",
            "ip_address": "192.168.1.1"
        },
        "payment_method": {
            "type": "credit_card",
            "last_four": "4242",
            "country_of_issue": "US"
        },
        "merchant": {
            "id": "merch_123",
            "name": "Test Store",
            "category": "retail"
        }
    }


def test_valid_transaction(valid_transaction):
    """Test that a valid transaction passes validation"""
    is_valid, message = validate_transaction_data(valid_transaction)
    assert is_valid is True
    assert message == "Valid"


def test_non_dict_input():
    """Test that non-dictionary input fails validation"""
    is_valid, message = validate_transaction_data("not a dict")
    assert is_valid is False
    assert "JSON object" in message


def test_missing_required_fields(valid_transaction):
    """Test that missing required fields fail validation"""
    # Test each required field
    required_fields = ["transaction_id", "timestamp", "amount", "currency", 
                      "customer", "payment_method", "merchant"]
    
    for field in required_fields:
        # Create a copy without the field being tested
        invalid_transaction = valid_transaction.copy()
        del invalid_transaction[field]
        
        is_valid, message = validate_transaction_data(invalid_transaction)
        assert is_valid is False
        assert f"Missing required field: {field}" in message


def test_invalid_amount_values(valid_transaction):
    """Test validation of various invalid amount values"""
    # Test negative amount
    transaction = valid_transaction.copy()
    transaction["amount"] = -50.00
    is_valid, message = validate_transaction_data(transaction)
    assert is_valid is False
    assert "positive number" in message
    
    # Test non-numeric string
    transaction = valid_transaction.copy()
    transaction["amount"] = "not-a-number"
    is_valid, message = validate_transaction_data(transaction)
    assert is_valid is False
    assert "valid number" in message


def test_missing_nested_fields(valid_transaction):
    """Test validation of missing nested structure fields"""
    # Test missing customer field
    transaction = valid_transaction.copy()
    transaction["customer"] = {"id": "cust_123", "country": "US"}  # Missing ip_address
    is_valid, message = validate_transaction_data(transaction)
    assert is_valid is False
    assert "Missing customer field" in message
    
    # Test missing payment_method field
    transaction = valid_transaction.copy()
    transaction["payment_method"] = {"type": "credit_card", "last_four": "4242"}  # Missing country_of_issue
    is_valid, message = validate_transaction_data(transaction)
    assert is_valid is False
    assert "Missing payment_method field" in message
    
    # Test missing merchant field
    transaction = valid_transaction.copy()
    transaction["merchant"] = {"id": "merch_123", "name": "Test Store"}  # Missing category
    is_valid, message = validate_transaction_data(transaction)
    assert is_valid is False
    assert "Missing merchant field" in message


if __name__ == "__main__":
    pytest.main(["-v"])
