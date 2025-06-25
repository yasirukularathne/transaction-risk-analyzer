# Transaction Risk Analyzer API Report

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [API Endpoints](#api-endpoints)
   - [Authentication](#authentication)
   - [REST Endpoints](#rest-endpoints)
   - [Test Endpoints](#test-endpoints)
   - [WebSocket Events](#websocket-events)
5. [Webhook Service](#webhook-service)
   - [Implementation Details](#webhook-implementation-details)
   - [Testing with Webhook Client](#webhook-client)
   - [Integration Guide](#integrating-external-systems)
6. [Data Models](#data-models)
   - [Transaction Model](#transaction-object)
   - [Notification Model](#notification-object)
   - [Risk Analysis Model](#risk-analysis-object)
7. [Example Transactions](#example-transactions)
   - [Successful Transaction](#successful-transaction-example)
   - [Failed Transaction](#failed-transaction-example)
8. [Error Handling](#error-handling)
9. [Troubleshooting](#troubleshooting)

## System Overview

The Transaction Risk Analyzer is a real-time financial transaction monitoring system designed to detect and alert administrators about high-risk transactions. It uses large language models (via the GROQ API) for intelligent risk assessment based on multiple factors including geographic patterns, transaction amounts, and merchant categories.

**Key Features:**

- Real-time transaction validation and risk analysis
- Intelligent risk scoring using LLM (GROQ API)
- WebSocket-based real-time notifications for high-risk transactions
- Administrative dashboard for transaction monitoring
- REST API for transaction processing and retrieval
- Webhook integration for external systems
- Support for cross-origin resource sharing (CORS)

## Architecture

The Transaction Risk Analyzer system consists of the following components:

1. **Backend (Python/Flask)**

   - REST API endpoints for transaction processing
   - WebSocket server for real-time notifications
   - Integration with GROQ API for LLM-based risk analysis
   - Authentication and validation layers
   - In-memory data storage for transactions and notifications

2. **Frontend (React)**

   - Administrative dashboard
   - Real-time transaction monitoring
   - WebSocket client for receiving alerts
   - Risk visualization with color coding
   - Transaction detail views

3. **External Services**

   - GROQ API for LLM-based transaction risk analysis

4. **Webhook Client**
   - Testing utility for simulating external system integration

## Setup Instructions

### Prerequisites

- Python 3.6+
- Node.js 12+ (for frontend)
- GROQ API key

### Backend Setup

1. **Install Python dependencies**

   ```
   pip install flask flask-cors flask-socketio python-dotenv requests pytest
   ```

2. **Configure Environment Variables**

   Create a `.env` file in the root directory with:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Start the Flask server**

   ```
   python Server.py
   ```

   The server will start at http://localhost:8081

### Frontend Setup

1. **Navigate to the frontend directory**

   ```
   cd transaction-risk-analyzer-ui
   ```

2. **Install dependencies**

   ```
   npm install
   ```

3. **Start the development server**

   ```
   npm start
   ```

   The frontend will be available at http://localhost:3000

## API Endpoints

### Authentication

All API endpoints use HTTP Basic Authentication:

- **Username**: admin
- **Password**: secret123
- **Header Format**: `Authorization: Basic YWRtaW46c2VjcmV0MTIz`

### REST Endpoints

#### 1. Process Transaction (Webhook)

Process a new transaction and analyze its risk.

- **URL**: `/webhook`
- **Method**: `POST`
- **Auth Required**: Yes
- **Headers**:
  - Content-Type: application/json
  - Authorization: Basic Authentication header
- **Request Body**:
  ```json
  {
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
  ```
- **Success Response**:
  ```json
  {
    "transaction_id": "tx_12345",
    "status": "processed",
    "risk_analysis": {
      "risk_score": 0.25,
      "risk_factors": ["large_amount"],
      "reasoning": "Transaction amount is higher than typical for this merchant category.",
      "recommended_action": "allow"
    },
    "timestamp": "2023-06-20T14:30:05Z"
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "Invalid transaction data: Missing required field: customer"
  }
  ```

#### 2. Get Admin Notifications

Retrieve high-risk transaction notifications.

- **URL**: `/admin/notifications`
- **Method**: `GET`
- **Auth Required**: Yes
- **Headers**:
  - Authorization: Basic Authentication header
- **Success Response**:
  ```json
  {
    "notifications": [
      {
        "transaction_id": "tx_12345",
        "timestamp": "2023-06-20T14:30:00Z",
        "amount": 1500.0,
        "currency": "USD",
        "alert_type": "high_risk_transaction",
        "status": "flagged",
        "admin_notification_sent": true,
        "risk_analysis": {
          "risk_score": 0.85,
          "risk_factors": ["high_risk_country", "large_amount"],
          "reasoning": "Transaction involves high-risk country and large amount.",
          "recommended_action": "block"
        },
        "customer": {
          "id": "cust_001",
          "country": "IR",
          "ip_address": "192.168.1.1"
        },
        "payment_method": {
          "type": "credit_card",
          "last_four": "1234",
          "country_of_issue": "IR"
        },
        "merchant": {
          "id": "merch_001",
          "name": "Online Electronics",
          "category": "electronics"
        }
      }
    ]
  }
  ```

#### 3. Get All Transactions

Retrieve all processed transactions (both high-risk and normal).

- **URL**: `/admin/all-transactions`
- **Method**: `GET`
- **Auth Required**: Yes
- **Headers**:
  - Authorization: Basic Authentication header
- **Success Response**:
  ```json
  {
    "transactions": [
      {
        "transaction_id": "tx_12345",
        "timestamp": "2023-06-20T14:30:00Z",
        "amount": 1500.0,
        "currency": "USD",
        "risk_analysis": {
          "risk_score": 0.25,
          "risk_factors": ["large_amount"],
          "reasoning": "Transaction amount is higher than typical for this merchant category.",
          "recommended_action": "allow"
        },
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
    ]
  }
  ```

### Test Endpoints

These endpoints are provided for testing and demonstration purposes:

#### 1. Test Standard Transaction

- **URL**: `/test-standard-transaction`
- **Method**: `POST`
- **Auth Required**: Yes

#### 2. Test High-Risk Country Transaction

- **URL**: `/test-high-risk-country`
- **Method**: `POST`
- **Auth Required**: Yes

#### 3. Test Missing Fields

- **URL**: `/test-missing-fields`
- **Method**: `POST`
- **Auth Required**: Yes

### WebSocket Events

#### Server to Client Events

1. **connection_established**

   - Emitted when a client connects to the WebSocket server

2. **new_transaction**
   - Emitted when a high-risk transaction is detected
   - Data includes the complete transaction object with risk analysis

## Webhook Service

The Transaction Risk Analyzer implements a robust webhook endpoint that accepts financial transaction data from external systems for risk analysis.

### Webhook Implementation Details

1. **Endpoint for POST Requests**

   - Endpoint: `/webhook`
   - Method: `POST`
   - Content Type: `application/json`

2. **Basic Authentication**

   - Username: `admin`
   - Password: `secret123`
   - Implementation extracts and validates Authorization header

3. **Transaction Data Validation**

   - Validates presence of all required fields
   - Checks for empty values in all required fields
   - Validates data types (e.g., numeric amount)

4. **HTTP Status Codes and Responses**
   - 200 OK: Successfully processed transaction
   - 400 Bad Request: Invalid transaction data
   - 401 Unauthorized: Authentication failed
   - 500 Internal Server Error: Server-side processing errors

### Webhook Client

The Transaction Risk Analyzer includes a webhook client utility (Webhook.py) for testing.

To use the webhook client:

1. **Configure transaction data**: Modify the transaction data in Webhook.py
2. **Run the client**: Execute `python Webhook.py`
3. **View results**: Console will display detailed response information

### Integrating External Systems

For production environments, external systems can integrate with the Transaction Risk Analyzer by:

1. Implementing HTTP POST requests to the webhook endpoint
2. Using Basic Authentication with configured credentials
3. Formatting transaction data according to the documented schema
4. Processing the response to determine risk status

## Data Models

### Transaction Object

A transaction contains:

- `transaction_id`: Unique identifier for the transaction
- `timestamp`: Date and time in ISO format
- `amount`: Numeric value of the transaction
- `currency`: Currency code (e.g., USD)
- `customer`: Object containing customer details
  - `id`: Customer identifier
  - `country`: Two-letter country code
  - `ip_address`: Customer's IP address
- `payment_method`: Object with payment method information
  - `type`: Payment method type (e.g., credit_card)
  - `last_four`: Last four digits of the card
  - `country_of_issue`: Two-letter country code
- `merchant`: Object with merchant details
  - `id`: Merchant identifier
  - `name`: Merchant name
  - `category`: Business category

### Notification Object

A notification includes:

- `transaction_id`: Unique identifier for the transaction
- `timestamp`: Date and time
- `amount`: Transaction amount
- `currency`: Currency code
- `alert_type`: Type of alert triggered
- `status`: Transaction status
- `admin_notification_sent`: Boolean flag
- `risk_analysis`: Risk analysis details
- `customer`: Customer information
- `payment_method`: Payment method details
- `merchant`: Merchant information
- `transaction_details`: Complete transaction data

### Risk Analysis Object

Risk analysis includes:

- `risk_score`: Number between 0.0 and 1.0 representing risk level
- `risk_factors`: Array of identified risk factors
- `reasoning`: Explanation of the risk assessment
- `recommended_action`: One of "allow", "review", or "block"

Risk threshold definitions:

- **Low Risk**: 0.0 - 0.3 (Action: Allow)
- **Medium Risk**: 0.3 - 0.7 (Action: Review)
- **High Risk**: 0.7 - 1.0 (Action: Block)

## Example Transactions

### Successful Transaction Example

**Request:**

```
POST /webhook HTTP/1.1
Host: localhost:8081
Content-Type: application/json
Authorization: Basic YWRtaW46c2VjcmV0MTIz

{
  "transaction_id": "tx_standard_001",
  "timestamp": "2023-06-20T14:30:00Z",
  "amount": 150.00,
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
```

**Response:**

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "transaction_id": "tx_standard_001",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.15,
    "risk_factors": [],
    "reasoning": "Transaction appears normal with no elevated risk factors.",
    "recommended_action": "allow"
  },
  "timestamp": "2023-06-20T14:30:05Z"
}
```

### Failed Transaction Example

**Request:**

```
POST /webhook HTTP/1.1
Host: localhost:8081
Content-Type: application/json
Authorization: Basic YWRtaW46c2VjcmV0MTIz

{
  "transaction_id": "tx_high_risk_001",
  "timestamp": "2023-06-20T14:30:00Z",
  "amount": 15000.00,
  "currency": "USD",
  "customer": {
    "id": "cust_002",
    "country": "RU",
    "ip_address": "185.220.100.240"
  },
  "payment_method": {
    "type": "credit_card",
    "last_four": "9999",
    "country_of_issue": "US"
  },
  "merchant": {
    "id": "merch_001",
    "name": "Online Electronics",
    "category": "electronics"
  }
}
```

**Response:**

```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "transaction_id": "tx_high_risk_001",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.85,
    "risk_factors": ["high_risk_country", "large_amount", "country_mismatch"],
    "reasoning": "Transaction involves high-risk country and unusually large amount.",
    "recommended_action": "block"
  },
  "timestamp": "2023-06-20T14:30:05Z",
  "admin_notification_sent": true,
  "alert_type": "high_risk_transaction"
}
```

## Error Handling

Common error codes:

- **400 Bad Request**: Invalid transaction data or JSON format
- **401 Unauthorized**: Missing or invalid authentication credentials
- **404 Not Found**: Endpoint does not exist
- **500 Internal Server Error**: Server-side processing error

Error responses are JSON objects containing an error description:

```json
{
  "error": "Description of the error"
}
```

## Troubleshooting

### CORS Issues

If experiencing CORS issues:

1. Verify frontend is running on port 3000
2. Check backend CORS configuration includes your frontend origin
3. Ensure WebSocket configuration allows your frontend origin

### WebSocket Connection Issues

If WebSocket connections are failing:

1. Verify correct URL: http://localhost:8081
2. Ensure withCredentials option is set to true
3. Check browser console for connection errors
4. Verify server is running on port 8081
5. Try both WebSocket and polling transports

### Authentication Issues

If API calls return 401 Unauthorized errors:

1. Ensure Basic Authentication header is properly formatted
2. Verify credentials are correct (username: admin, password: secret123)
3. Check if credentials: 'include' option is set for cross-origin fetch requests

### Backend Server Issues

If backend server fails to start:

1. Verify Python dependencies are installed
2. Check .env file exists with valid GROQ API key
3. Make sure port 8081 is not already in use
4. Check server logs for specific error messages
   "category": "retail"
   }
   }

````

- **Success Response** (Standard Transaction):
  - **Code**: 200 OK
  - **Content Example**:

```json
{
  "transaction_id": "tx_123456",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.25,
    "risk_factors": ["Standard transaction"],
    "reasoning": "This appears to be a normal transaction with no risk factors identified.",
    "recommended_action": "allow"
  },
  "timestamp": "2025-06-24T15:45:30Z"
}
````

- **Success Response** (High-Risk Transaction):
  - **Code**: 200 OK
  - **Content Example**:

```json
{
  "transaction_id": "tx_123456",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.85,
    "risk_factors": ["Cross-border payment", "High-risk country"],
    "reasoning": "Transaction originates from high-risk country with unusual payment pattern.",
    "recommended_action": "block"
  },
  "timestamp": "2025-06-24T15:45:30Z",
  "admin_notification_sent": true,
  "alert_type": "high_risk_transaction"
}
```

#### 2.2.2 Get Admin Notifications

Retrieves notifications for high-risk transactions.

- **URL**: `/admin/notifications`
- **Method**: GET
- **Auth Required**: Yes
- **Headers**:

  - `Authorization: Basic YWRtaW46c2VjcmV0MTIz`

- **Success Response**:
  - **Code**: 200 OK
  - **Content Example**:

```json
{
  "notifications": [
    {
      "transaction_id": "tx_12345",
      "timestamp": "2025-06-24T14:30:00Z",
      "amount": 5000,
      "currency": "USD",
      "alert_type": "high_risk_transaction",
      "status": "flagged",
      "admin_notification_sent": true,
      "risk_analysis": {
        "risk_score": 0.85,
        "risk_factors": ["High amount", "Unusual location"],
        "reasoning": "Transaction shows suspicious pattern.",
        "recommended_action": "block"
      },
      "customer": {
        "id": "cust_12345",
        "country": "US",
        "ip_address": "185.220.100.240"
      },
      "payment_method": {
        "type": "credit_card",
        "last_four": "9999",
        "country_of_issue": "RU"
      },
      "merchant": {
        "id": "merch_12345",
        "name": "Luxury Store",
        "category": "jewelry"
      }
    }
  ]
}
```

#### 2.2.3 Get All Transactions

Retrieves all processed transactions (both high-risk and normal).

- **URL**: `/admin/all-transactions`
- **Method**: GET
- **Auth Required**: Yes
- **Headers**:

  - `Authorization: Basic YWRtaW46c2VjcmV0MTIz`

- **Success Response**:
  - **Code**: 200 OK
  - **Content Example**:

```json
{
  "transactions": [
    {
      "transaction_id": "tx_123456",
      "timestamp": "2025-06-20T14:30:45Z",
      "amount": 199.99,
      "currency": "USD",
      "risk_analysis": {
        "risk_score": 0.25,
        "risk_factors": ["Standard transaction"],
        "reasoning": "No risk factors identified.",
        "recommended_action": "allow"
      },
      "customer": {
        "id": "cust_12345",
        "country": "US",
        "ip_address": "192.168.1.1"
      },
      "payment_method": {
        "type": "credit_card",
        "last_four": "1234",
        "country_of_issue": "US"
      },
      "merchant": {
        "id": "merch_12345",
        "name": "Example Store",
        "category": "retail"
      }
    },
    {
      "transaction_id": "tx_123457",
      "timestamp": "2025-06-20T15:00:00Z",
      "amount": 5000,
      "currency": "USD",
      "risk_analysis": {
        "risk_score": 0.85,
        "risk_factors": ["High amount", "Unusual location"],
        "reasoning": "Transaction shows suspicious pattern.",
        "recommended_action": "block"
      },
      "customer": {
        "id": "cust_12346",
        "country": "US",
        "ip_address": "185.220.100.240"
      },
      "payment_method": {
        "type": "credit_card",
        "last_four": "9999",
        "country_of_issue": "RU"
      },
      "merchant": {
        "id": "merch_12346",
        "name": "Luxury Store",
        "category": "jewelry"
      }
    }
  ]
}
```

### 2.3 Test Endpoints

These endpoints are provided for testing and demonstration purposes.

#### 2.3.1 Test Standard Transaction

- **URL**: `/test-standard-transaction`
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - `Authorization: Basic YWRtaW46c2VjcmV0MTIz`

- **Response Example**:
  - **Code**: 200 OK
  - **Content**:

```json
{
  "message": "Standard transaction processed",
  "transaction": {
    "transaction_id": "tx_test_001",
    "timestamp": "2025-06-24T12:30:00Z",
    "amount": 50.0,
    "currency": "USD",
    "customer": {
      "id": "cust_test_001",
      "country": "US",
      "ip_address": "192.168.1.100"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "1234",
      "country_of_issue": "US"
    },
    "merchant": {
      "id": "merch_test_001",
      "name": "Test Store",
      "category": "retail"
    }
  },
  "risk_analysis": {
    "risk_score": 0.15,
    "risk_factors": ["Standard transaction"],
    "reasoning": "This appears to be a normal transaction with no risk factors identified.",
    "recommended_action": "allow"
  }
}
```

#### 2.3.2 Test High-Risk Country Transaction

- **URL**: `/test-high-risk-country`
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - `Authorization: Basic YWRtaW46c2VjcmV0MTIz`

- **Response Example**:
  - **Code**: 200 OK
  - **Content**:

```json
{
  "message": "High-risk country transaction processed",
  "transaction": {
    "transaction_id": "tx_test_002",
    "timestamp": "2025-06-24T12:35:00Z",
    "amount": 500.0,
    "currency": "USD",
    "customer": {
      "id": "cust_test_002",
      "country": "US",
      "ip_address": "192.168.1.100"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "5678",
      "country_of_issue": "RU"
    },
    "merchant": {
      "id": "merch_test_002",
      "name": "Test Store",
      "category": "electronics"
    }
  },
  "risk_analysis": {
    "risk_score": 0.8,
    "risk_factors": ["Cross-border payment", "High-risk country"],
    "reasoning": "Transaction originates from high-risk country Russia.",
    "recommended_action": "block"
  },
  "notification_sent": true
}
```

#### 2.3.3 Test Missing Fields

- **URL**: `/test-missing-fields`
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - `Authorization: Basic YWRtaW46c2VjcmV0MTIz`

- **Response Example**:
  - **Code**: 200 OK
  - **Content**:

```json
{
  "message": "Missing fields validation test",
  "transaction": {
    "transaction_id": "tx_test_003",
    "timestamp": "2025-06-24T12:40:00Z",
    "amount": 75.0,
    "currency": "USD",
    "customer": {
      "id": "cust_test_003",
      "country": "",
      "ip_address": "192.168.1.100"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "9012",
      "country_of_issue": "US"
    },
    "merchant": {
      "id": "merch_test_003",
      "name": "Test Store",
      "category": "services"
    }
  },
  "is_valid": false,
  "validation_message": "Empty value for customer field: country"
}
```

## 3. Examples of Successful and Failed Transactions

### 3.1 Successful Transactions

#### 3.1.1 Standard Low-Risk Transaction

**Request:**

```json
{
  "transaction_id": "tx_success_001",
  "timestamp": "2025-06-24T10:15:30Z",
  "amount": 89.95,
  "currency": "USD",
  "customer": {
    "id": "cust_regular_001",
    "country": "US",
    "ip_address": "192.168.1.50"
  },
  "payment_method": {
    "type": "credit_card",
    "last_four": "4242",
    "country_of_issue": "US"
  },
  "merchant": {
    "id": "merch_bookstore_001",
    "name": "Online Bookstore",
    "category": "books"
  }
}
```

**Response:**

```json
{
  "transaction_id": "tx_success_001",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.12,
    "risk_factors": ["Standard transaction"],
    "reasoning": "This appears to be a normal transaction with no risk factors identified. Common merchant category and reasonable amount.",
    "recommended_action": "allow"
  },
  "timestamp": "2025-06-24T10:15:35Z"
}
```

#### 3.1.2 Medium-Risk Transaction (Approved but Flagged)

**Request:**

```json
{
  "transaction_id": "tx_success_002",
  "timestamp": "2025-06-24T11:20:15Z",
  "amount": 1250.0,
  "currency": "USD",
  "customer": {
    "id": "cust_regular_002",
    "country": "US",
    "ip_address": "203.0.113.42"
  },
  "payment_method": {
    "type": "credit_card",
    "last_four": "8888",
    "country_of_issue": "CA"
  },
  "merchant": {
    "id": "merch_electronics_001",
    "name": "Premium Electronics",
    "category": "electronics"
  }
}
```

**Response:**

```json
{
  "transaction_id": "tx_success_002",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.45,
    "risk_factors": ["Higher than average amount", "Cross-border payment"],
    "reasoning": "Transaction amount is higher than average for this merchant category, and payment method is from a different country than the customer.",
    "recommended_action": "review"
  },
  "timestamp": "2025-06-24T11:20:18Z"
}
```

### 3.2 Failed Transactions

#### 3.2.1 Authentication Failure

**Request:**

```
curl -X POST "http://localhost:8081/webhook" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Basic aW52YWxpZDppbnZhbGlk" \\
  -d '{
    "transaction_id": "tx_fail_001",
    "timestamp": "2025-06-24T13:05:22Z",
    "amount": 50.00,
    "currency": "USD",
    "customer": {
      "id": "cust_fail_001",
      "country": "US",
      "ip_address": "192.168.1.20"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "1111",
      "country_of_issue": "US"
    },
    "merchant": {
      "id": "merch_fail_001",
      "name": "Test Merchant",
      "category": "retail"
    }
  }'
```

**Response:**

```json
{
  "error": "Unauthorized"
}
```

**Status Code:** 401 Unauthorized

#### 3.2.2 Missing Required Fields

**Request:**

```json
{
  "transaction_id": "tx_fail_002",
  "timestamp": "2025-06-24T14:10:05Z",
  "amount": 75.5,
  "currency": "USD",
  "customer": {
    "id": "cust_fail_002",
    "country": "US"
    /* Missing ip_address field */
  },
  "payment_method": {
    "type": "credit_card",
    "last_four": "2222",
    "country_of_issue": "US"
  },
  "merchant": {
    "id": "merch_fail_002",
    "name": "Another Merchant",
    "category": "food"
  }
}
```

**Response:**

```json
{
  "error": "Invalid transaction data: Missing customer field: ip_address"
}
```

**Status Code:** 400 Bad Request

#### 3.2.3 High-Risk Transaction (Blocked)

**Request:**

```json
{
  "transaction_id": "tx_fail_003",
  "timestamp": "2025-06-24T15:30:12Z",
  "amount": 9999.99,
  "currency": "USD",
  "customer": {
    "id": "cust_fail_003",
    "country": "US",
    "ip_address": "185.220.100.250"
  },
  "payment_method": {
    "type": "credit_card",
    "last_four": "3333",
    "country_of_issue": "IR"
  },
  "merchant": {
    "id": "merch_fail_003",
    "name": "Luxury Watches",
    "category": "jewelry"
  }
}
```

**Response:**

```json
{
  "transaction_id": "tx_fail_003",
  "status": "processed",
  "risk_analysis": {
    "risk_score": 0.95,
    "risk_factors": [
      "High amount",
      "High-risk country payment method",
      "Suspicious IP address",
      "High-value merchandise"
    ],
    "reasoning": "Transaction originates from a suspicious IP address with a payment method from a high-risk country (Iran). The transaction amount is unusually high for a first-time customer.",
    "recommended_action": "block"
  },
  "timestamp": "2025-06-24T15:30:15Z",
  "admin_notification_sent": true,
  "alert_type": "high_risk_transaction"
}
```

**Note:** While this transaction technically returns a 200 status code, it is considered a failed transaction from a business perspective as the recommended action is to block it.

#### 3.2.4 Invalid JSON Format

**Request:**

```
curl -X POST "http://localhost:8081/webhook" \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Basic YWRtaW46c2VjcmV0MTIz" \\
  -d '{
    "transaction_id": "tx_fail_004",
    "timestamp": "2025-06-24T16:45:30Z",
    "amount": "not-a-number",
    "currency": "USD",
    ...
  }'
```

**Response:**

```json
{
  "error": "Invalid transaction data: Amount must be a valid number"
}
```

**Status Code:** 400 Bad Request

## 4. Setup and Running Instructions

### 4.1 Prerequisites

Before installing and running the Transaction Risk Analyzer, ensure you have the following prerequisites installed:

- Python 3.6+
- Node.js 12+ (for frontend)
- GROQ API key (for LLM-based risk analysis)

### 4.2 Backend Setup

1. **Clone the Repository**

   ```
   git clone https://github.com/your-username/transaction-risk-analyzer.git
   cd transaction-risk-analyzer
   ```

2. **Install Python Dependencies**

   ```
   pip install flask flask-cors flask-socketio python-dotenv requests pytest
   ```

   Or use the provided batch file:

   ```
   install_dependencies.bat
   ```

3. **Configure Environment Variables**

   Create a `.env` file in the root directory containing:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   WEBHOOK_USERNAME=admin
   WEBHOOK_PASSWORD=secret123
   ```

4. **Start the Flask Server**
   ```
   python Server.py
   ```
   The server will start on port 8081 and will be accessible at http://localhost:8081.

### 4.3 Frontend Setup

1. **Navigate to the Frontend Directory**

   ```
   cd transaction-risk-analyzer-ui
   ```

2. **Install Required Libraries**

   The Transaction Risk Analyzer frontend requires the following libraries:

   - **UI Framework**: Material UI (@mui/material, @emotion/react, @emotion/styled, @mui/icons-material)
   - **Core Libraries**: React (react, react-dom)
   - **Routing**: React Router (react-router-dom)
   - **WebSocket Communication**: Socket.IO Client (socket.io-client)
   - **Schema Validation**: Ajv (ajv)
   - **Testing Tools**: Jest and React Testing Library

   Install all dependencies with:

   ```
   npm install @mui/material @mui/icons-material @emotion/react @emotion/styled react react-dom react-router-dom socket.io-client ajv react-scripts
   ```

   Or simply run:

   ```
   npm install
   ```

   This will install all dependencies specified in the package.json file.

3. **Start the React Development Server**

   ```
   npm start
   ```

   The frontend will be accessible at http://localhost:3000 by default.

   Alternatively, you can specify a different port:

   ```
   npm start -- --port 3001
   ```

### 4.4 Testing the System

#### 4.4.1 Using the Webhook Client

1. **Run the Webhook Client**

   ```
   python Webhook.py
   ```

   This will send a sample transaction to the webhook endpoint using the default authentication credentials.

2. **Modify Transaction Data**

   To test different scenarios, modify the `transaction_data` variable in `Webhook.py`.

#### 4.4.2 Using cURL

You can also test the API using cURL:

```
curl -X POST "http://localhost:8081/webhook" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46c2VjcmV0MTIz" \
  -d '{
    "transaction_id": "tx_curl_test_001",
    "timestamp": "2025-06-24T15:30:00Z",
    "amount": 123.45,
    "currency": "USD",
    "customer": {
      "id": "cust_curl_001",
      "country": "US",
      "ip_address": "192.168.1.100"
    },
    "payment_method": {
      "type": "credit_card",
      "last_four": "1234",
      "country_of_issue": "US"
    },
    "merchant": {
      "id": "merch_curl_001",
      "name": "Test Merchant",
      "category": "retail"
    }
  }'
```

#### 4.4.3 Using Test Endpoints

The system provides several test endpoints for easy testing:

- `/test-standard-transaction`: Tests a standard low-risk transaction
- `/test-high-risk-country`: Tests a transaction from a high-risk country
- `/test-missing-fields`: Tests a transaction with missing fields

Example:

```
curl -X POST "http://localhost:8081/test-standard-transaction" \
  -H "Authorization: Basic YWRtaW46c2VjcmV0MTIz"
```

### 4.5 Monitoring the System

1. **Access the Admin Dashboard**

   Open a web browser and navigate to http://localhost:3000 to access the admin dashboard.

2. **View Real-Time Notifications**

   The admin dashboard will display real-time notifications for high-risk transactions via WebSocket.

3. **Review Transaction History**

   Use the dashboard to review all processed transactions and their risk assessments.

## 5. Common Issues and Troubleshooting

### 5.1 CORS Issues

If you experience CORS (Cross-Origin Resource Sharing) issues:

1. Verify the frontend is running on either port 3000 or 3001
2. Check that the backend CORS configuration includes your frontend origin
3. Ensure the WebSocket configuration allows your frontend origin

### 5.2 WebSocket Connection Issues

If WebSocket connections are failing:

1. Verify the correct URL is being used: http://localhost:8081
2. Ensure the withCredentials option is set to true
3. Check browser console for connection errors
4. Verify the server is running and listening on port 8081

### 5.3 Authentication Issues

If API calls return 401 Unauthorized errors:

1. Ensure the Basic Authentication header is properly formatted
2. Verify the credentials are correct (username: admin, password: secret123)
3. Check if the credentials: 'include' option is set for cross-origin fetch requests

### 5.4 Backend Server Issues

If the backend server fails to start:

1. Verify Python dependencies are installed
2. Check the .env file exists with a valid GROQ API key
3. Make sure port 8081 is not already in use
4. Check the server logs for specific error messages

## 6. Conclusion

The Transaction Risk Analyzer provides a robust API for processing and analyzing financial transactions. This report has documented the API endpoints, provided examples of successful and failed transactions, and included detailed setup instructions. By following these guidelines, you should be able to set up, run, and integrate with the Transaction Risk Analyzer system effectively.
