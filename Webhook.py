import requests
import json
from requests.auth import HTTPBasicAuth

# Configuration
URL = "http://127.0.0.1:8081/webhook"
USERNAME = "admin"
PASSWORD = "secret123"

# Transaction data
transaction_data =   {
    "transaction_id": "tx_12345",
    "timestamp": "2023-06-20T14:30:00Z",
    "amount": 1500.0,
    "currency": "USD",
    "customer": {
      "id": "cust_001",
      "country": "US",
      "ip_address": "192.168.1.1"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "1234",
      "country_of_issue": "US"
    },
    "merchant": {
      "id": "merch_001",
      "name": "Online Electronics",
      "category": "electronics"
    }
  }


def send_webhook_request():
    """Send POST request to the webhook endpoint"""
    try:
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Send POST request with Basic Auth
        print(f"Sending POST request to: {URL}")
        print(f"Transaction ID: {transaction_data['transaction_id']}")
        print(f"Amount: ${transaction_data['amount']:,}")
        
        response = requests.post(
            url=URL,
            json=transaction_data,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers=headers,
            timeout=30
        )
        
        # Print response details
        print(f"\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Try to parse JSON response
        try:
            response_json = response.json()
            print(f"Response Body:")
            print(json.dumps(response_json, indent=2))
            
            # Check for risk analysis
            if 'risk_analysis' in response_json:
                risk_analysis = response_json['risk_analysis']
                print(f"\n--- Risk Analysis ---")
                print(f"Risk Score: {risk_analysis.get('risk_score', 'N/A')}")
                print(f"Recommended Action: {risk_analysis.get('recommended_action', 'N/A')}")
                print(f"Risk Factors: {risk_analysis.get('risk_factors', [])}")
                print(f"Reasoning: {risk_analysis.get('reasoning', 'N/A')}")
                
        except json.JSONDecodeError:
            print(f"Response Body (raw text):")
            print(response.text)
        
        # Check if request was successful
        if response.status_code == 200:
            print(f"\n✅ Request successful!")
        else:
            print(f"\n❌ Request failed with status code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {URL}")
        print("Make sure your Flask server is running on http://127.0.0.1:8081")
    except requests.exceptions.Timeout:
        print(f"❌ Timeout Error: Request took too long")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    print("🚀 Sending webhook request...")
    send_webhook_request()