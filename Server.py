from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps
import base64
import requests
import json
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit
NOTIFICATIONS = []
ALL_TRANSACTIONS = []  # Store all processed transactions, not just high-risk ones


# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HIGH_RISK_COUNTRIES = ['RU', 'IR', 'KP', 'VE', 'MM']

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Basic Authentication Decorator
def require_basic_auth(username, password):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Basic '):
                try:
                    encoded_credentials = auth_header.split(' ')[1]
                    decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
                    incoming_user, incoming_pass = decoded_credentials.split(':')
                    if incoming_user == username and incoming_pass == password:
                        return f(*args, **kwargs)
                except Exception:
                    pass
            return jsonify({'error': 'Unauthorized'}), 401
        return decorated_function
    return decorator

def build_optimized_groq_prompt(transaction):
    """Build an optimized prompt for GROQ API based on transaction data"""
    transaction_json = json.dumps(transaction, indent=2)
    
    prompt_text = f"""You are a financial risk analyst. Evaluate this transaction and return a risk score (0.0-1.0).

Transaction Data:
{transaction_json}

Consider these risk factors:
- Geographic anomalies (high-risk countries(['RU', 'IR', 'KP', 'VE', 'MM'] vs customer country vs payment country ))
- Unusual amounts for merchant category
- Payment method risks
- IP/location inconsistencies
- Merchant category and typical fraud rates 
- Merchant's history and reputation


Respond ONLY in this JSON format:
{{
    "risk_score": 0.0,
    "risk_factors": ["list", "of", "factors"],
    "reasoning": "brief explanation",
    "recommended_action": "allow|review|block"
}}

Risk thresholds: 0.0-0.3 = allow, 0.3-0.7 = review, 0.7-1.0 = block"""
    
    return {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.1,
        "max_tokens": 300
    }

def call_groq_api(transaction_data):
    """Call GROQ API with proper endpoint and error handling"""
    if not GROQ_API_KEY:
        logger.warning("GROQ API key not configured")
        return {
            "risk_score": 0.5,
            "risk_factors": ["API configuration error"],
            "reasoning": "GROQ API key not configured",
            "recommended_action": "review"
        }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = build_optimized_groq_prompt(transaction_data)
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(prompt), timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            try:
                # Clean the content - remove markdown formatting if present
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                parsed_result = json.loads(content)
                
                # Validate and sanitize the response
                risk_score = float(parsed_result.get("risk_score", 0.5))
                risk_score = max(0.0, min(1.0, risk_score))  # Clamp between 0 and 1
                
                risk_factors = parsed_result.get("risk_factors", [])
                if not isinstance(risk_factors, list):
                    risk_factors = ["Analysis completed"]
                
                reasoning = parsed_result.get("reasoning", "Risk analysis completed")
                
                action = parsed_result.get("recommended_action", "review").lower()
                if action not in ["allow", "review", "block"]:
                    action = "review"
                
                return {
                    "risk_score": risk_score,
                    "risk_factors": risk_factors,
                    "reasoning": reasoning,
                    "recommended_action": action
                }
                    
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.error(f"Failed to parse LLM response: {e}")
                return {
                    "risk_score": 0.5,
                    "risk_factors": ["LLM parsing error"],
                    "reasoning": f"Could not parse model response: {content[:100]}...",
                    "recommended_action": "review"
                }
        else:
            raise ValueError("Unexpected response format from GROQ API")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {
            "risk_score": 0.5,
            "risk_factors": ["API error"],
            "reasoning": f"Failed to analyze: {str(e)}",
            "recommended_action": "review"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            "risk_score": 0.7,
            "risk_factors": ["Processing error"],
            "reasoning": f"Error during analysis: {str(e)}",
            "recommended_action": "review"
        }

def validate_transaction_data(data):
    """Validate that transaction data has required structure"""
    if not isinstance(data, dict):
        return False, "Data must be a JSON object"
    
    # Required top-level fields
    required_fields = ["transaction_id", "timestamp", "amount", "currency", "customer", "payment_method", "merchant"]
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        # Also check for empty values
        if data[field] == "" or data[field] is None:
            return False, f"Empty value for required field: {field}"
        
     # Validate amount is a valid number
    try:
        amount = float(data["amount"])
        if not (isinstance(amount, (int, float)) and amount >= 0 and amount < float('inf')):
            return False, "Amount must be a valid positive number"
        data["amount"] = amount  # Convert to float
    except (ValueError, TypeError):
        return False, "Amount must be a valid number"
    
    # Validate customer structure
    customer = data.get("customer", {})
    customer_fields = ["id", "country", "ip_address"]
    for field in customer_fields:
        if field not in customer:
            return False, f"Missing customer field: {field}"
        # Check for empty values
        if customer[field] == "" or customer[field] is None:
            return False, f"Empty value for customer field: {field}"
    
    # Validate payment_method structure
    payment_method = data.get("payment_method", {})
    payment_fields = ["type", "last_four", "country_of_issue"]
    for field in payment_fields:
        if field not in payment_method:
            return False, f"Missing payment_method field: {field}"
        # Check for empty values
        if payment_method[field] == "" or payment_method[field] is None:
            return False, f"Empty value for payment_method field: {field}"
    
    # Validate merchant structure
    merchant = data.get("merchant", {})
    merchant_fields = ["id", "name", "category"]
    for field in merchant_fields:
        if field not in merchant:
            return False, f"Missing merchant field: {field}"
        # Check for empty values
        if merchant[field] == "" or merchant[field] is None:
            return False, f"Empty value for merchant field: {field}"
    
    # Validate data types
    try:
        float(data["amount"])
    except (ValueError, TypeError):
        return False, "Amount must be a valid number"
    
    return True, "Valid"

def send_admin_notification(transaction_data, risk_analysis):
    """Send notification to administrators for high-risk transactions"""
    risk_score = risk_analysis.get("risk_score", 0)
    
    # Check for high-risk countries
    customer_country = transaction_data.get("customer", {}).get("country")
    payment_country = transaction_data.get("payment_method", {}).get("country_of_issue")
    
    # Force high risk if countries involved are in the high-risk list
    if customer_country in HIGH_RISK_COUNTRIES or payment_country in HIGH_RISK_COUNTRIES:
        risk_score = max(risk_score, 0.8)  # Ensure it's flagged as high risk
        # Add high-risk country factor if not already present
        risk_factors = risk_analysis.get("risk_factors", [])
        high_risk_country_factor = f"Transaction involves high-risk country: {customer_country if customer_country in HIGH_RISK_COUNTRIES else payment_country}"
        if not any(factor.startswith("Transaction involves high-risk country") for factor in risk_factors):
            risk_factors.append(high_risk_country_factor)
            risk_analysis["risk_factors"] = risk_factors
            risk_analysis["recommended_action"] = "block"
    
    # Only notify for high-risk transactions (score >= 0.7)
        # Create notification in the format expected by frontend
        notification = {
            "transaction_id": transaction_data.get("transaction_id"),
            "timestamp": transaction_data.get("timestamp"),
            "amount": transaction_data.get("amount"),
            "currency": transaction_data.get("currency"),
            "alert_type": "high_risk_transaction",
            "status": "flagged",
            "admin_notification_sent": True,
            "risk_analysis": {
                "risk_score": risk_analysis.get("risk_score"),
                "risk_factors": risk_analysis.get("risk_factors", []),
                "reasoning": risk_analysis.get("reasoning", ""),
                "recommended_action": risk_analysis.get("recommended_action", "review")
            },
            # Include full transaction details for expanded view
            "customer": transaction_data.get("customer", {}),
            "payment_method": transaction_data.get("payment_method", {}),
            "merchant": transaction_data.get("merchant", {}),
            "transaction_details": transaction_data  # Keep original for reference
        }
        
        logger.warning(f"HIGH RISK TRANSACTION DETECTED: {notification['transaction_id']}")
        NOTIFICATIONS.append(notification)  # Store notification in memory
        
        # Emit the notification to all connected clients
        socketio.emit('new_transaction', notification)
        logger.info(f"Notification sent via Socket.IO for transaction: {notification['transaction_id']}")
        
        return notification
    
    return None



# ✅ Main webhook endpoint
@app.route('/webhook', methods=['POST'])
@require_basic_auth("admin", "secret123")
def webhook():
    """Main webhook endpoint for processing transactions"""
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    logger.info(f"Received transaction: {data.get('transaction_id', 'unknown')}")

    # Validate transaction data
    is_valid, validation_message = validate_transaction_data(data)
    if not is_valid:
        logger.warning(f"Invalid transaction data: {validation_message}")
        return jsonify({"error": f"Invalid transaction data: {validation_message}"}), 400

    transaction_id = data.get('transaction_id')
    logger.info(f"Processing transaction: {transaction_id}")
      # Analyze transaction with GROQ
    risk_analysis = call_groq_api(data)
    admin_notification = send_admin_notification(data, risk_analysis)
    
    # Build response
    response = {
        "transaction_id": transaction_id,
        "status": "processed",
        "risk_analysis": risk_analysis,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    # Include notification info if sent
    if admin_notification:
        response["admin_notification_sent"] = True
        response["alert_type"] = admin_notification["alert_type"]
    
    # Store transaction in ALL_TRANSACTIONS for history
    transaction_record = {
        "transaction_id": transaction_id,
        "timestamp": data.get("timestamp", datetime.utcnow().isoformat() + "Z"),
        "amount": data.get("amount"),
        "currency": data.get("currency"),
        "risk_analysis": risk_analysis,
        "customer": data.get("customer", {}),
        "payment_method": data.get("payment_method", {}),
        "merchant": data.get("merchant", {})
    }
    ALL_TRANSACTIONS.append(transaction_record)
    
    return jsonify(response), 200

# ✅ Admin notification endpoint (for testing/viewing notifications)
@app.route('/admin/notifications', methods=['GET'])
@require_basic_auth("admin", "secret123")
def get_notifications():
    """Endpoint to retrieve recent notifications"""
    return jsonify({
        "notifications": NOTIFICATIONS
    })

# ✅ All transactions endpoint (for transaction history)
@app.route('/admin/all-transactions', methods=['GET'])
@require_basic_auth("admin", "secret123")
def get_all_transactions():
    """Endpoint to retrieve all transactions processed by the system"""
    return jsonify({
        "transactions": ALL_TRANSACTIONS
    })

# ✅ Test endpoint for transactions with missing fields
@app.route('/test-missing-fields', methods=['POST'])
@require_basic_auth("admin", "secret123")
def test_missing_fields():
    """Test endpoint to simulate a transaction with missing or empty fields"""
    # This transaction has empty values that should trigger validation errors
    test_transaction = {
        "transaction_id": "tx_missing_fields_" + str(int(datetime.utcnow().timestamp())),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "amount": 100.00,
        "currency": "USD",
        "customer": {
            "id": "cust_test_003",
            "country": "",  # Empty country
            "ip_address": "192.168.1.1"
        },
        "payment_method": {
            "type": "",  # Empty payment type
            "last_four": "4321",
            "country_of_issue": "US"
        },
        "merchant": {
            "id": "merch_test_003",
            "name": "Test Merchant",
            "category": "retail"
        }
    }
    
    # Attempt to validate - should fail
    is_valid, validation_message = validate_transaction_data(test_transaction)
    
    return jsonify({
        "message": "Missing fields validation test",
        "transaction": test_transaction,
        "is_valid": is_valid,
        "validation_message": validation_message
    })

# ✅ Test endpoint to simulate a standard transaction
@app.route('/test-standard-transaction', methods=['POST'])
@require_basic_auth("admin", "secret123")
def test_standard_transaction():
    """Test endpoint to simulate a standard low-risk transaction"""
    test_transaction = {
        "transaction_id": "tx_standard_" + str(int(datetime.utcnow().timestamp())),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "amount": 59.99,
        "currency": "USD",
        "customer": {
            "id": "cust_regular_001",
            "country": "US",
            "ip_address": "192.168.0.1"
        },
        "payment_method": {
            "type": "credit_card",
            "last_four": "1234",
            "country_of_issue": "US"
        },
        "merchant": {
            "id": "merch_online_001",
            "name": "Online Retailer",
            "category": "electronics"
        }
    }
    
    # Validate and process the transaction
    is_valid, validation_message = validate_transaction_data(test_transaction)
    if not is_valid:
        return jsonify({"error": f"Invalid test transaction: {validation_message}"}), 400
        
    # Analyze transaction with GROQ
    risk_analysis = call_groq_api(test_transaction)
    admin_notification = send_admin_notification(test_transaction, risk_analysis)
    
    # Add to transaction history
    transaction_record = {
        **test_transaction,
        "risk_analysis": risk_analysis,
        "status": "processed",
    }
    ALL_TRANSACTIONS.append(transaction_record)
    
    return jsonify({
        "message": "Standard transaction processed",
        "transaction": test_transaction,
        "risk_analysis": risk_analysis
    })
    
# ✅ Test endpoint to simulate high-risk country transaction
@app.route('/test-high-risk-country', methods=['POST'])
@require_basic_auth("admin", "secret123")
def test_high_risk_country():
    """Test endpoint to simulate a transaction from a high-risk country"""
    test_transaction = {
        "transaction_id": "tx_highrisk_country_" + str(int(datetime.utcnow().timestamp())),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "amount": 2500.00,
        "currency": "USD",
        "customer": {
            "id": "cust_test_002",
            "country": "RU",  # High-risk country
            "ip_address": "95.31.18.119"
        },
        "payment_method": {
            "type": "credit_card",
            "last_four": "1234",
            "country_of_issue": "RU"
        },
        "merchant": {
            "id": "merch_test_002",
            "name": "Test Merchant",
            "category": "electronics"
        }
    }
    
    # Validate and process the transaction
    is_valid, validation_message = validate_transaction_data(test_transaction)
    if not is_valid:
        return jsonify({"error": f"Invalid test transaction: {validation_message}"}), 400
        
    # Analyze transaction with GROQ
    risk_analysis = call_groq_api(test_transaction)
    admin_notification = send_admin_notification(test_transaction, risk_analysis)
    
    # Add to transaction history
    transaction_record = {
        **test_transaction,
        "risk_analysis": risk_analysis,
        "status": "processed",
    }
    ALL_TRANSACTIONS.append(transaction_record)
    
    return jsonify({
        "message": "High-risk country transaction processed",
        "transaction": test_transaction,
        "risk_analysis": risk_analysis,
        "notification_sent": admin_notification is not None
    })

# ✅ Socket.IO connection handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connection_established', {'message': 'Connected to risk monitoring system'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

# ✅ Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/webhook",
            "/admin/notifications", 
            "/admin/all-transactions",
            "/test-notification",
            "/test-standard-transaction",
            "/test-high-risk-country",
            "/test-missing-fields"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

# ✅ Run the Flask server
if __name__ == '__main__':
    print("🚀 Starting Transaction Risk Analyzer...")
    print(f"🔑 GROQ API Key configured: {bool(GROQ_API_KEY)}")
    print("📋 Test the API with:")
    print("   POST /webhook - Process transactions (requires Basic Auth)")
    print("   GET  /admin/notifications - Get high-risk notifications (requires Basic Auth)")
    print("   GET  /admin/all-transactions - Get all transactions (requires Basic Auth)")
    print("   POST /test-notification - Send test notification (requires Basic Auth)")
    print("   POST /test-standard-transaction - Test standard transaction (requires Basic Auth)")
    print("   POST /test-high-risk-country - Test high-risk country detection (requires Basic Auth)")
    print("   POST /test-missing-fields - Test missing fields validation (requires Basic Auth)")
    print("   Credentials: admin:secret123")
    socketio.run(app, host='0.0.0.0', port=8081, debug=True)