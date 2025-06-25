import React, { useState, useEffect, useRef } from "react";
import io from "socket.io-client";
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
} from "@mui/material";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import "./AdminDashboard.css";

// Risk Transaction Row Component
const RiskTransactionRow = ({ transaction }) => {
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
      </TableRow>
      <TableRow>
        <TableCell className="collapsed-cell" colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box className="detail-box">
              <Typography variant="h6" gutterBottom component="div">
                Risk Analysis Details
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
              <Box className="transaction-details">
                <Typography variant="subtitle1" gutterBottom>
                  Transaction Details:
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
                        Alert Type
                      </TableCell>
                      <TableCell>{transaction.alert_type}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">
                        Status
                      </TableCell>
                      <TableCell>{transaction.status}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </Box>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

// Main Dashboard Component
const AdminDashboard = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [socket, setSocket] = useState(null);
  const audioRef = useRef(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const newSocket = io("http://localhost:8081");
    setSocket(newSocket);

    return () => newSocket.close();
  }, []);
  // Listen for new transactions
  useEffect(() => {
    if (!socket) return;

    socket.on("new_transaction", (transaction) => {
      setTransactions((prev) => [transaction, ...prev]);
      // Play sound alert when a new transaction notification is received
      if (audioRef.current) {
        audioRef.current.play().catch((err) => {
          console.error("Failed to play sound alert:", err);
        });
      }
    });

    return () => {
      socket.off("new_transaction");
    };
  }, [socket]);

  // Fetch transactions from server
  const fetchTransactions = async () => {
    try {
      const response = await fetch(
        "http://localhost:8081/admin/notifications",
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
      setTransactions(data.notifications || []);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
      console.error("Fetch error:", err);
    }
  };

  // Initial and periodic fetch
  useEffect(() => {
    fetchTransactions();
    const interval = setInterval(fetchTransactions, 30000); // every 30 sec
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
    <Box className="dashboard-container">
      {/* Audio element for notification sound */}
      <audio ref={audioRef} src="/sounds/notification.mp3" preload="auto" />

      <Typography variant="h4" gutterBottom>
        Risk Transaction Monitor
      </Typography>

      {error && (
        <Alert severity="error" className="error-alert">
          {error}
        </Alert>
      )}

      <Card>
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
                </TableRow>
              </TableHead>
              <TableBody>
                {transactions.length > 0 ? (
                  transactions.map((transaction) => (
                    <RiskTransactionRow
                      key={transaction.transaction_id}
                      transaction={transaction}
                    />
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      No high-risk transactions found
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

export default AdminDashboard;
