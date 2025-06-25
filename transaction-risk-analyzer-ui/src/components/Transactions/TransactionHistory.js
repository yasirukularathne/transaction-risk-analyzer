import React, { useState, useEffect } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Chip,
  IconButton,
  Collapse,
  CircularProgress,
  TextField,
  MenuItem,
  Grid,
  Select,
  FormControl,
  InputLabel,
} from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import "./TransactionHistory.css";

// Transaction Row Component
const TransactionRow = ({ transaction }) => {
  const [open, setOpen] = useState(false);

  // Add validation for risk analysis data
  const riskScore = transaction?.risk_analysis?.risk_score ?? 0;
  const riskFactors = transaction?.risk_analysis?.risk_factors ?? [];
  const recommendedAction =
    transaction?.risk_analysis?.recommended_action ?? "review";
  const reasoning = transaction?.risk_analysis?.reasoning ?? "";

  const getRiskColor = (score) => {
    if (score <= 0.3) return "success";
    if (score <= 0.7) return "warning";
    return "error";
  };

  return (
    <>
      <TableRow className="row-no-border">
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{transaction?.transaction_id ?? "N/A"}</TableCell>
        <TableCell>
          <Chip
            label={`Risk: ${riskScore.toFixed(2)}`}
            color={getRiskColor(riskScore)}
            size="small"
          />
        </TableCell>
        <TableCell>
          {new Date(transaction?.timestamp).toLocaleString()}
        </TableCell>
        <TableCell>
          {transaction?.amount ?? 0} {transaction?.currency ?? "USD"}
        </TableCell>
        <TableCell>{transaction?.customer?.country ?? "Unknown"}</TableCell>
        <TableCell>{transaction?.merchant?.name ?? "Unknown"}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell className="collapsed-cell" colSpan={7}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box className="detail-box">
              <Typography variant="h6" gutterBottom component="div">
                Transaction Details
              </Typography>

              {/* Risk Score and Action */}
              <Box className="risk-analysis-box">
                <Chip
                  label={`Risk Score: ${riskScore.toFixed(2)}`}
                  color={getRiskColor(riskScore)}
                />
                <Chip
                  label={`Action: ${recommendedAction.toUpperCase()}`}
                  color={
                    recommendedAction === "block"
                      ? "error"
                      : recommendedAction === "review"
                      ? "warning"
                      : "success"
                  }
                />
                {transaction.admin_notification_sent && (
                  <Chip label="Admin Notified" color="info" />
                )}
              </Box>

              {/* Risk Factors */}
              <Typography variant="subtitle1" gutterBottom>
                Risk Factors:
              </Typography>
              <Box className="risk-factors-container">
                {riskFactors.map((factor, index) => (
                  <Chip
                    key={index}
                    label={factor}
                    variant="outlined"
                    size="small"
                    className="risk-factor-chip"
                  />
                ))}
              </Box>

              {/* Reasoning */}
              <Typography variant="subtitle1" gutterBottom>
                Analysis:
              </Typography>
              <Paper className="analysis-paper">
                <Typography variant="body2">{reasoning}</Typography>
              </Paper>

              {/* Transaction Details */}
              <Grid container spacing={2} className="transaction-details">
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Transaction Information:
                  </Typography>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Transaction ID
                        </TableCell>
                        <TableCell>{transaction.transaction_id}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Timestamp
                        </TableCell>
                        <TableCell>
                          {new Date(transaction.timestamp).toLocaleString()}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Amount
                        </TableCell>
                        <TableCell>
                          {transaction.amount} {transaction.currency}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Customer Details:
                  </Typography>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Customer ID
                        </TableCell>
                        <TableCell>{transaction.customer?.id}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Country
                        </TableCell>
                        <TableCell>{transaction.customer?.country}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          IP Address
                        </TableCell>
                        <TableCell>
                          {transaction.customer?.ip_address}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Payment Details:
                  </Typography>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Payment Type
                        </TableCell>
                        <TableCell>
                          {transaction.payment_method?.type}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Last Four
                        </TableCell>
                        <TableCell>
                          {transaction.payment_method?.last_four}
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Card Country
                        </TableCell>
                        <TableCell>
                          {transaction.payment_method?.country_of_issue}
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Merchant Details:
                  </Typography>
                  <Table size="small">
                    <TableBody>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Merchant ID
                        </TableCell>
                        <TableCell>{transaction.merchant?.id}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Merchant Name
                        </TableCell>
                        <TableCell>{transaction.merchant?.name}</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell component="th" scope="row">
                          Category
                        </TableCell>
                        <TableCell>{transaction.merchant?.category}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </Grid>
              </Grid>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

// Main TransactionHistory Component
const TransactionHistory = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    riskLevel: "all",
    searchTerm: "",
  });
  // Fetch All Transactions from server (including normal transactions)
  const fetchAllTransactions = async () => {
    try {
      // Use the dedicated all-transactions endpoint for transaction history
      const response = await fetch(
        "http://localhost:8081/admin/all-transactions",
        {
          headers: {
            Authorization: `Basic ${btoa("admin:secret123")}`,
            "Content-Type": "application/json",
          },
          credentials: "include",
          mode: "cors",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch transactions");
      }

      const data = await response.json();

      // Set transactions from the dedicated endpoint
      setTransactions(data.transactions || []);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      console.error("Fetch error:", err);
    }
  };

  // Handle filter changes
  const handleFilterChange = (event) => {
    setFilters({
      ...filters,
      [event.target.name]: event.target.value,
    });
  };

  // Filter transactions based on current filters
  const filteredTransactions = transactions.filter((transaction) => {
    // Risk level filter
    if (filters.riskLevel !== "all" && transaction?.risk_analysis?.risk_score) {
      const score = transaction.risk_analysis.risk_score;
      if (filters.riskLevel === "low" && score > 0.3) return false;
      if (filters.riskLevel === "medium" && (score <= 0.3 || score > 0.7))
        return false;
      if (filters.riskLevel === "high" && score <= 0.7) return false;
    }

    // Search term filter (searches in transaction ID, merchant name, or customer ID)
    if (filters.searchTerm) {
      const searchLower = filters.searchTerm.toLowerCase();
      return (
        transaction.transaction_id?.toLowerCase().includes(searchLower) ||
        transaction.merchant?.name?.toLowerCase().includes(searchLower) ||
        transaction.customer?.id?.toLowerCase().includes(searchLower)
      );
    }

    return true;
  });

  // Initial fetch
  useEffect(() => {
    fetchAllTransactions();
    const interval = setInterval(fetchAllTransactions, 60000); // every 60 sec
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box className="loading-container">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="transaction-history-container">
      <Typography variant="h4" gutterBottom>
        Transaction History
      </Typography>

      {error && (
        <Alert severity="error" className="error-alert">
          {error}
        </Alert>
      )}

      {/* Filter controls */}
      <Card className="filter-card">
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                label="Search"
                name="searchTerm"
                variant="outlined"
                size="small"
                value={filters.searchTerm}
                onChange={handleFilterChange}
                placeholder="Search by ID, merchant..."
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Risk Level</InputLabel>
                <Select
                  name="riskLevel"
                  value={filters.riskLevel}
                  onChange={handleFilterChange}
                  label="Risk Level"
                >
                  <MenuItem value="all">All Levels</MenuItem>
                  <MenuItem value="low">Low Risk (0.0-0.3)</MenuItem>
                  <MenuItem value="medium">Medium Risk (0.3-0.7)</MenuItem>
                  <MenuItem value="high">High Risk (0.7-1.0)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card className="transaction-card">
        <CardContent>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell />
                  <TableCell>Transaction ID</TableCell>
                  <TableCell>Risk Score</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Country</TableCell>
                  <TableCell>Merchant</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredTransactions.length > 0 ? (
                  filteredTransactions.map((transaction) => (
                    <TransactionRow
                      key={transaction.transaction_id}
                      transaction={transaction}
                    />
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      No transactions found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TransactionHistory;
