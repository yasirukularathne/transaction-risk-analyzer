# Transaction Risk Analyzer - Quick Start Guide

This guide provides instructions for setting up, running, and testing the Transaction Risk Analyzer system.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running the Application](#running-the-application)
5. [Testing the System](#testing-the-system)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.6+** installed
- **Node.js 12+** installed
- **GROQ API key** (obtain from [https://console.groq.com/](https://console.groq.com/))
- **Git** (optional, for cloning the repository)

## Backend Setup

1. **Clone or download the repository** (if not already done)

2. **Navigate to the project directory**
   ```
   cd transaction-risk-analyzer
   ```

3. **Install Python dependencies**
   
   Using the provided batch file (Windows):
   ```
   install_dependencies.bat
   ```
   
   Or manually with pip:
   ```
   pip install flask flask-cors flask-socketio python-dotenv requests pytest
   ```

4. **Configure the GROQ API key**
   
   Create a file named `.env` in the root directory with:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Frontend Setup

1. **Navigate to the frontend directory**
   ```
   cd transaction-risk-analyzer-ui
   ```

2. **Install Node.js dependencies**
   ```
   npm install
   ```

3. **Configure notification sound** (optional)
   
   Using the provided batch file (Windows):
   ```
   cd ..
   download_notification_sound.bat
   ```

## Running the Application

1. **Start the backend server**
   
   In the main project directory:
   ```
   python Server.py
   ```
   
   You should see output confirming the server is running on port 8081.

2. **Start the frontend development server**
   
   Open a new terminal, navigate to the frontend directory, and run:
   ```
   npm start
   ```
   
   This will start the React development server and automatically open the application in your browser at http://localhost:3000

3. **Access the application**
   
   - Risk Transaction Monitor: http://localhost:3000/admin
   - All Transactions View: http://localhost:3000/transactions

## Testing the System

### Manual Testing

1. **Generate a test high-risk notification**
   
   Open a new terminal and run:
   ```
   curl -u admin:secret123 -X POST http://localhost:8081/test-notification
   ```
   
   This will create a sample high-risk transaction that should appear in the admin dashboard with a sound alert.

2. **Send a test transaction**
   
   You can use the provided Webhook.py script:
   ```
   python Webhook.py
   ```
   
   This sends a test transaction to the webhook endpoint for processing.

3. **View all transactions**
   ```
   curl -u admin:secret123 http://localhost:8081/admin/all-transactions
   ```

### Running Automated Tests

The system includes comprehensive test files:

1. **Run all tests**
   ```
   run_tests.bat
   ```
   Or manually:
   ```
   python -m pytest Test.py -v
   ```

2. **Run specific test categories**
   ```
   run_validation_tests.bat     # Data validation tests
   run_auth_tests.bat           # Authentication tests
   run_groq_api_tests.bat       # API integration tests
   run_admin_notification_tests.bat  # Notification tests
   run_webhook_tests.bat        # Webhook endpoint tests
   ```

## Troubleshooting

### Common Issues

1. **Server won't start**
   - Check if port 8081 is already in use
   - Verify Python dependencies are installed
   - Check for syntax errors in Server.py

2. **Authentication errors**
   - Default credentials are admin:secret123
   - Make sure Authorization header is formatted correctly

3. **GROQ API errors**
   - Confirm API key is set correctly in the .env file
   - Check internet connection and GROQ service status

4. **WebSocket connection issues**
   - Ensure both backend and frontend servers are running
   - Check browser console for connection errors

### Getting More Help

- Check the API Documentation (API_DOCUMENTATION.md)
- Review test files for examples of expected behavior
- Examine server logs for error messages

## Next Steps

After setting up the system, you can:

1. Explore the API endpoints as documented in API_DOCUMENTATION.md
2. Review transaction examples to understand risk detection
3. Test high-risk transaction scenarios
4. Customize the risk factors and thresholds
