import React, { useState } from "react";
import { TextField, Button, Paper, Typography, Alert } from "@mui/material";

interface LoginProps {
  onLogin: (data: any) => Promise<void>;
}

function LoginComponent({ onLogin }: LoginProps) {
  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });
  const [errorMsg, setErrorMsg] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: any) => {
    const { name, value } = e.target;
    setLoginData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const validateForm = () => {
    if (!loginData.email || !loginData.password) {
      setErrorMsg("All fields are required");
      return false;
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(loginData.email)) {
      setErrorMsg("Invalid email format");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setErrorMsg("");

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await onLogin(loginData);
    } catch (error: any) {
      setErrorMsg(error.message || "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        backgroundColor: "#f5f5f5",
      }}
    >
      <Paper style={{ padding: "40px", maxWidth: "400px", width: "100%" }}>
        <Typography variant="h4" align="center" gutterBottom>
          Task Manager Login
        </Typography>

        <Typography
          variant="body2"
          align="center"
          color="textSecondary"
          style={{ marginBottom: "30px" }}
        >
          Please sign in to access your dashboard
        </Typography>

        {errorMsg && (
          <Alert severity="error" style={{ marginBottom: "20px" }}>
            {errorMsg}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          <TextField
            fullWidth
            name="email"
            label="Email Address"
            type="email"
            value={loginData.email}
            onChange={handleChange}
            style={{ marginBottom: "20px" }}
            disabled={isLoading}
          />

          <TextField
            fullWidth
            name="password"
            label="Password"
            type="password"
            value={loginData.password}
            onChange={handleChange}
            style={{ marginBottom: "30px" }}
            disabled={isLoading}
          />

          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={isLoading}
            style={{ marginBottom: "20px" }}
          >
            {isLoading ? "Logging in..." : "Login"}
          </Button>
        </form>

        <div style={{ textAlign: "center", marginTop: "20px" }}>
          <Typography variant="body2" color="textSecondary">
            Test Account:
          </Typography>
          <Typography variant="body2">Email: demo@taskdashboard.com</Typography>
          <Typography variant="body2">Password: demo123</Typography>
        </div>
      </Paper>
    </div>
  );
}

export default LoginComponent;
