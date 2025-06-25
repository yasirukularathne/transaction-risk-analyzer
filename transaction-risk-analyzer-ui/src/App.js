import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import {
  Box,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
} from "@mui/material";

import AdminDashboard from "./components/Admin/AdminDashboard";
import TransactionHistory from "./components/Transactions/TransactionHistory";

function App() {
  return (
    <Router>
      <CssBaseline />

      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Transaction Risk Analyzer
          </Typography>
          <Button color="inherit" component={Link} to="/admin">
            Risk Dashboard
          </Button>
          <Button color="inherit" component={Link} to="/transactions">
            All Transactions
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        <Box sx={{ mt: 2 }}>
          <Routes>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/transactions" element={<TransactionHistory />} />
          </Routes>
        </Box>
      </Container>
    </Router>
  );
}

export default App;
