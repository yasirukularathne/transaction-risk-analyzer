# Transaction Risk Analyzer: Complete API Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Setup Instructions](#setup-instructions)
4. [Backend API Reference](#backend-api-reference)
   - [Authentication](#authentication)
   - [REST Endpoints](#rest-endpoints)
   - [Test Endpoints](#test-endpoints)
   - [WebSocket Events](#websocket-events)
5. [Frontend Application](#frontend-application)
   - [Components](#components)
   - [API Integration](#api-integration)
   - [WebSocket Integration](#websocket-integration)
6. [Webhook Service](#webhook-service)
7. [Transaction Data Models](#transaction-data-models)
8. [Risk Analysis Models](#risk-analysis-models)
9. [Error Handling](#error-handling)
10. [Example Transactions](#example-transactions)
11. [Troubleshooting](#troubleshooting)

## System Overview

The Transaction Risk Analyzer is a real-time financial transaction monitoring system designed to detect and alert administrators about high-risk transactions. It uses large language models (via the GROQ API) for intelligent risk assessment based on multiple factors including geographic patterns, transaction amounts, and merchant categories.

**Key Features:**

- Real-time transaction validation and risk analysis
- Intelligent risk scoring using LLM (GROQ API)
- WebSocket-based real-time notifications for high-risk transactions
- Administrative dashboard for transaction monitoring
- REST API for transaction processing and retrieval
- Support for cross-origin resource sharing (CORS)
- Webhook client for testing and integration with external systems

Components:

1. **Flask Backend**: Processes transactions, communicates with GROQ API, and broadcasts notifications
2. **React Frontend**: Displays transaction data and receives real-time notifications
3. **GROQ API**: External service providing LLM-based transaction risk analysis
4. **Webhook Client**: Python utility for testing transactions and demonstrating API integration

## Setup Instructions

### Prerequisites

- Python 3.6+
- Node.js 12+ (for frontend)
- GROQ API key

### Backend Setup

1. **Install Python dependencies**

   Install the necessary Python packages including Flask, Flask-CORS, Flask-SocketIO, python-dotenv, requests, and pytest using pip or the provided batch file (install_dependencies.bat).

2. **Configure Environment Variables**

   Create a `.env` file in the root directory containing the following variables:

   - GROQ_API_KEY: Your personal GROQ API key for transaction analysis
   - WEBHOOK_USERNAME: Username for webhook authentication (default: admin)
   - WEBHOOK_PASSWORD: Password for webhook authentication (default: secret123)

3. **Start the Flask server**

   Run the Server.py script to start the Flask server. The server will start on port 8081 and will be accessible at http://localhost:8081.

4. **Using the Webhook Client (Optional)**

   To test the transaction risk analysis system, you can run the Webhook.py script which will send a sample transaction to the webhook endpoint using the configured authentication credentials from your .env file.

### Frontend Setup

1. **Navigate to the frontend directory**

   Change to the transaction-risk-analyzer-ui directory to work with the frontend application.

2. **Install Node.js dependencies**

   Install all required npm packages for the React frontend using the npm install command.

3. **Start the React development server**

   Launch the React development server using npm start. The frontend will be accessible at http://localhost:3000 by default. Alternatively, you can specify a different port if needed, such as port 3001. The backend is configured to accept connections from both http://localhost:3000 and http://localhost:3001.

## Backend API Reference

### Authentication

All API endpoints use HTTP Basic Authentication:

- **Username**: admin
- **Password**: secret123
- **Header Format**: Basic Authentication header with base64 encoded credentials

### REST Endpoints

### 1. Process Transaction (Webhook)

Process a new transaction and analyze its risk.

- **URL**: /webhook
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - Content-Type: application/json
  - Authorization: Basic Authentication header

- **Request Body**:
  A JSON object containing transaction details including transaction_id, timestamp, amount, currency, customer information (id, country, IP address), payment method details (type, last four digits, country of issue), and merchant information (id, name, category).

- **Success Response**:
  For standard transactions, the system responds with HTTP 200 and provides the transaction ID, processed status, risk analysis (containing risk score, factors, reasoning, and recommended action), and timestamp.

  For high-risk transactions, the response includes the same information plus flags indicating that admin notification was sent and the alert type.

- **Error Response**:
  - HTTP 400: For invalid transaction data, with an error message specifying the problem
  - HTTP 401: For unauthorized access attempts

### 2. Get Admin Notifications

Retrieve high-risk transaction notifications.

- **URL**: /admin/notifications
- **Method**: GET
- **Auth Required**: Yes
- **Headers**:

  - Authorization: Basic Authentication header

- **Success Response**:
  Returns a list of notifications for high-risk transactions, including transaction details, risk analysis, customer information, payment method details, and merchant data.

### 3. Get All Transactions

Retrieve all processed transactions (both high-risk and normal).

- **URL**: /admin/all-transactions
- **Method**: GET
- **Auth Required**: Yes
- **Headers**:

  - Authorization: Basic Authentication header

- **Response**:
  Returns an array of transaction records including transaction IDs, timestamps, amounts, currencies, risk analyses, customer details, payment methods, and merchant information.

- **Status Codes**:
  - 200 OK: Transactions retrieved
  - 401 Unauthorized: Authentication failed

### Test Endpoints

These endpoints are provided for testing and demonstration purposes:

#### 1. Test Standard Transaction

Simulate a standard low-risk transaction.

- **URL**: /test-standard-transaction
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - Authorization: Basic Authentication header

- **Response**:
  Returns a message confirming the standard transaction was processed, along with the transaction data and risk analysis information.

#### 2. Test High-Risk Country Transaction

Simulate a transaction from a high-risk country.

- **URL**: /test-high-risk-country
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - Authorization: Basic Authentication header

- **Response**:
  Returns a message confirming the high-risk country transaction was processed, with transaction data, risk analysis, and confirmation that a notification was sent.

#### 3. Test Missing Fields

Simulate a transaction with missing or empty fields.

- **URL**: /test-missing-fields
- **Method**: POST
- **Auth Required**: Yes
- **Headers**:

  - Authorization: Basic Authentication header

- **Response**:
  Returns a message about the missing fields validation test, the incomplete transaction data, validation status (false), and the validation error message.

## Transaction Data Models

### Transaction Object

A transaction contains the following information:

- transaction_id: Unique identifier for the transaction
- timestamp: Date and time in ISO format
- amount: Numeric value of the transaction
- currency: Currency code (e.g., USD)
- customer: Object containing customer details
- payment_method: Object with payment method information
- merchant: Object with merchant details

The Customer object includes:

- id: Customer identifier
- country: Two-letter country code
- ip_address: Customer's IP address

The PaymentMethod object includes:

- type: Payment method type (e.g., credit_card)
- last_four: Last four digits of the card
- country_of_issue: Two-letter country code for the issuing country

The Merchant object includes:

- id: Merchant identifier
- name: Merchant name
- category: Business category

### Notification Object

A notification includes:

- transaction_id: Unique identifier for the transaction
- timestamp: Date and time
- amount: Transaction amount
- currency: Currency code
- alert_type: Type of alert triggered
- status: Transaction status
- admin_notification_sent: Boolean flag
- risk_analysis: Risk analysis details
- customer: Customer information
- payment_method: Payment method details
- merchant: Merchant information
- transaction_details: Complete transaction data

## Risk Analysis Models

### Risk Analysis Object

Risk analysis includes:

- risk_score: Number between 0.0 and 1.0 representing risk level
- risk_factors: Array of identified risk factors
- reasoning: Explanation of the risk assessment
- recommended_action: One of "allow", "review", or "block"

### Risk Threshold Definitions

- **Low Risk**: 0.0 - 0.3 (Action: Allow)
- **Medium Risk**: 0.3 - 0.7 (Action: Review)
- **High Risk**: 0.7 - 1.0 (Action: Block)

### High-Risk Countries

The application defines the following countries as high-risk:

- RU (Russia)
- IR (Iran)
- KP (North Korea)
- VE (Venezuela)
- MM (Myanmar/Burma)

Transactions involving these countries are automatically flagged as high-risk.

## Error Handling

### Common Error Codes

- **400 Bad Request**: Invalid transaction data or JSON format
- **401 Unauthorized**: Missing or invalid authentication credentials
- **404 Not Found**: Endpoint does not exist
- **500 Internal Server Error**: Server-side processing error

### Error Response Format

Error responses are JSON objects containing an error description.

### WebSocket Events

The server emits and listens for the following WebSocket events:

#### Server to Client Events

1. **connection_established**

   - Emitted when a client connects to the WebSocket server
   - Data includes a connection confirmation message

2. **new_transaction**
   - Emitted when a high-risk transaction is detected
   - Data includes the complete transaction object with risk analysis

#### Client to Server Events

Currently, the server only processes incoming connections but does not handle custom client events.

### Client-Side Example

The frontend can connect to the WebSocket server, listen for connection establishment, receive real-time notifications of high-risk transactions, and handle connection errors. This notification system enables real-time monitoring of high-risk transactions without requiring manual refreshes.

## Frontend Application

### Components

The frontend application is built with React and includes the following main components:

#### 1. AdminDashboard (`src/components/Admin/AdminDashboard.js`)

Main administrative interface with the following features:

- Real-time transaction alerts via WebSocket
- Risk score visualization with color coding
- Detailed transaction view
- Transaction approval/rejection controls

#### 2. Navigation and Layout Components

- Header component with navigation links
- Sidebar with filtering options
- Main content area for transaction display

#### 3. Transaction Components

- Transaction list component
- Transaction detail component
- Risk score indicator component

### API Integration

#### Fetch Notifications Example

The frontend application fetches notifications from the backend by making an authenticated GET request to the notifications endpoint. The function handles errors and returns the notification data.

#### Fetch All Transactions Example

Similarly, the frontend fetches all transaction records from the all-transactions endpoint using proper authentication and error handling.

### WebSocket Integration

#### Connect to WebSocket Server

The AdminDashboard component establishes a WebSocket connection to receive real-time transaction alerts. It:

- Initializes a Socket.IO connection with proper credentials
- Sets up event listeners for connection events
- Handles incoming high-risk transaction notifications
- Displays alerts to administrators
- Properly cleans up the connection when unmounting

## Troubleshooting

### CORS Issues

If you experience CORS (Cross-Origin Resource Sharing) issues:

1. Verify the frontend is running on either port 3000 or 3001
2. Check that the backend CORS configuration includes your frontend origin
3. Ensure the WebSocket configuration allows your frontend origin

### WebSocket Connection Issues

If WebSocket connections are failing:

1. Verify the correct URL is being used: http://localhost:8081
2. Ensure the withCredentials option is set to true
3. Check browser console for connection errors
4. Verify the server is running and listening on port 8081
5. Try both WebSocket and polling transports if needed

### Authentication Issues

If API calls return 401 Unauthorized errors:

1. Ensure the Basic Authentication header is properly formatted
2. Verify the credentials are correct (username: admin, password: secret123)
3. Check if the credentials: 'include' option is set for cross-origin fetch requests

### Backend Server Issues

If the backend server fails to start:

1. Verify Python dependencies are installed
2. Check the .env file exists with a valid GROQ API key
3. Make sure port 8081 is not already in use
4. Check the server logs for specific error messages
5. Verify that Flask and Flask-SocketIO versions are compatible

## Webhook Service

The Transaction Risk Analyzer implements a robust webhook endpoint that accepts financial transaction data from external systems for risk analysis. This service is complemented by a webhook client utility (Webhook.py) for testing.

### Webhook Implementation Details

The webhook implementation satisfies these key requirements:

1. **Endpoint for POST Requests**

   - Endpoint: /webhook
   - Method: POST
   - Content Type: application/json
   - Implementation: Flask route handler in Server.py

2. **Basic Authentication**

   - Username: admin
   - Password: secret123
   - Implementation includes:
     - Extracting the Authorization header
     - Decoding Base64 credentials
     - Validating against configured username and password
     - Returning 401 Unauthorized if authentication fails

3. **Transaction Data Validation**

   - Validates presence of all required fields:
     - transaction_id, timestamp, amount, currency
     - customer with id, country, ip_address
     - payment_method with type, last_four, country_of_issue
     - merchant with id, name, category
   - Checks for empty values in all required fields
   - Validates data types (e.g., numeric amount)

4. **HTTP Status Codes and Responses**
   - 200 OK: Successfully processed transaction (with risk analysis)
   - 400 Bad Request: Invalid transaction data (with error message)
   - 401 Unauthorized: Authentication failed
   - 500 Internal Server Error: Server-side processing errors

### Webhook Client

The Transaction Risk Analyzer includes a webhook client utility (Webhook.py) that allows you to send test transactions to the backend API for processing and risk analysis.

### Usage

To use the webhook client:

1. **Configure transaction data**: Modify the transaction data in Webhook.py to test different scenarios
2. **Run the client**: Execute the Webhook.py script
3. **View results**: The client will display detailed response information including risk analysis

### Using the Webhook Service

#### Command-Line Testing with cURL

You can test the webhook endpoint using cURL by sending a POST request to the webhook URL with the appropriate headers and a JSON payload containing transaction data.

#### Integration from External Systems

External payment systems can integrate with the Transaction Risk Analyzer by sending HTTP requests with proper authentication and formatted transaction data. The integration code would:

1. Send the transaction data to the webhook endpoint
2. Process the response based on risk analysis
3. Take appropriate action (allow, review, or block) based on the recommended action

### Webhook Service Flow

The complete flow of the webhook service:

1. **External System**: Sends transaction data to webhook endpoint with authentication
2. **Authentication Layer**: Validates credentials using Basic Auth
3. **Validation Layer**: Checks transaction data structure and values
4. **Risk Analysis Layer**: Processes valid transactions through the GROQ API
5. **Notification Layer**: Sends alerts for high-risk transactions via WebSocket
6. **Response Layer**: Returns analysis results with appropriate status code
7. **Storage Layer**: Stores the transaction and analysis in the transaction history

This modular approach ensures each step of transaction processing is properly handled with appropriate error reporting and response codes.

### Implementation

The webhook client is implemented in Python using the requests library. It:

1. Configures connection parameters
2. Prepares headers and authentication
3. Sends the transaction data to the webhook endpoint
4. Processes the response, checking the status code
5. Displays risk analysis information if the request is successful
6. Provides error messages for connection or processing failures

### Sample Webhook Transaction

You can use a sample transaction that includes all required fields: transaction ID, timestamp, amount, currency, customer information, payment method details, and merchant data.

### Testing Different Scenarios

You can modify the transaction data to test various scenarios:

1. **Standard Transaction**: Use normal values for all fields
2. **High-Risk Country**: Set country fields to high-risk countries (RU, IR, KP, VE, MM)
3. **Missing Fields**: Remove required fields to test validation
4. **Empty Values**: Set values to empty strings to test validation
5. **Large Amounts**: Test with unusually large transaction amounts

### Integrating External Systems

For production environments, external systems can integrate with the Transaction Risk Analyzer by:

1. Implementing HTTP POST requests to the webhook endpoint
2. Using Basic Authentication with the configured credentials
3. Formatting transaction data according to the documented schema
4. Processing the response to determine transaction status and risk analysis

### Implementation Details

The webhook implementation includes:

1. A Flask route handler for the webhook endpoint that:

   - Verifies JSON content
   - Logs incoming transactions
   - Validates transaction data
   - Processes transactions through the GROQ API
   - Sends admin notifications if needed
   - Builds appropriate responses
   - Stores transaction records

2. A Basic Authentication decorator that:

   - Extracts and verifies authorization headers
   - Processes encoded credentials
   - Validates username and password
   - Returns appropriate authorization responses

3. A transaction data validator that:
   - Checks for required fields
   - Validates data types
   - Ensures no empty values
   - Validates nested objects
   - Returns validation status and messages
