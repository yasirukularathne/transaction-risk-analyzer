# Transaction Risk Analyzer

A real-time financial transaction risk analysis and monitoring system with LLM integration.

## Overview

The Transaction Risk Analyzer is a full-stack application designed to process financial transactions, analyze them for risk factors using large language models, and provide real-time notifications for high-risk transactions. The system includes:

- REST API for transaction processing and data retrieval
- LLM-based risk assessment via GROQ API
- Real-time WebSocket notifications for high-risk transactions
- Web dashboard for monitoring transactions and alerts
- Comprehensive input validation and error handling

## Features

- **Transaction Processing**: Validates and processes financial transaction data
- **Risk Analysis**: Evaluates transactions using the GROQ LLM API
- **Real-time Monitoring**: WebSocket-based notifications for high-risk transactions
- **High-Risk Country Detection**: Special handling for transactions from high-risk countries
- **Admin Dashboard**: View all transactions and get alerted about high-risk activities
- **Sound Alerts**: Audio notifications for high-risk transactions

## Getting Started

See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for detailed setup and usage instructions.

### Quick Setup

1. Install backend dependencies:
   ```
   install_dependencies.bat
   ```

2. Set up .env file with:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. Start the Flask server:
   ```
   python Server.py
   ```

4. Set up the frontend:
   ```
   cd transaction-risk-analyzer-ui
   npm install
   npm start
   ```

## API Documentation

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## Testing

The system includes comprehensive test suites and example transactions:

- Use `run_tests.bat` to run all tests
- Use `test_example_transactions.bat` to test with predefined transaction examples
- See the `examples/` directory for sample transaction data

## High-Risk Detection

The system detects high-risk transactions based on multiple factors:

1. **Risk Score**: Transactions with a risk score >= 0.7 are flagged as high-risk
2. **High-Risk Countries**: Transactions involving countries in the high-risk list are automatically flagged
3. **LLM Analysis**: The GROQ LLM evaluates multiple risk factors including:
   - Geographic anomalies
   - Unusual transaction amounts
   - Payment method risks
   - IP/location inconsistencies
   - Merchant category fraud rates

## License

This project is licensed for internal use only. All rights reserved.

## Contributing

To contribute to this project, please contact the project maintainer.
