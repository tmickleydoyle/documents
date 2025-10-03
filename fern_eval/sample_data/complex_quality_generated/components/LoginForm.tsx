import React, { useState, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Avatar,
  Divider,
  Link,
  InputAdornment,
  IconButton,
} from "@mui/material";
import {
  LockOutlined as LockIcon,
  Visibility,
  VisibilityOff,
} from "@mui/icons-material";
import { useForm, Controller } from "react-hook-form";

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginFormProps {
  onLogin: (credentials: LoginCredentials) => Promise<void>;
  loading?: boolean;
}

const LoginForm: React.FC<LoginFormProps> = ({ onLogin, loading = false }) => {
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);

  const formControls = useForm<LoginCredentials>({
    defaultValues: {
      email: "",
      password: "",
    },
    mode: "onChange",
  });

  const { control, handleSubmit, formState } = formControls;
  const { errors, isSubmitting } = formState;

  // Handle form submission
  const handleFormSubmit = useCallback(
    async (formData: LoginCredentials) => {
      setErrorMessage("");

      try {
        await onLogin(formData);
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Login failed. Please try again.";
        setErrorMessage(message);
      }
    },
    [onLogin]
  );

  // Toggle password visibility
  const handleTogglePasswordVisibility = useCallback(() => {
    setShowPassword((prev) => !prev);
  }, []);

  // Clear error when user starts typing
  const handleClearError = useCallback(() => {
    if (errorMessage) {
      setErrorMessage("");
    }
  }, [errorMessage]);

  const isFormLoading = loading || isSubmitting;

  // Email validation rules
  const emailValidation = {
    required: "Email is required",
    pattern: {
      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: "Please enter a valid email address",
    },
  };

  // Password validation rules
  const passwordValidation = {
    required: "Password is required",
    minLength: {
      value: 6,
      message: "Password must be at least 6 characters",
    },
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "grey.50",
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 400, width: "100%", boxShadow: 3 }}>
        <CardContent sx={{ p: 4 }}>
          {/* Header Section */}
          <Box display="flex" flexDirection="column" alignItems="center" mb={3}>
            <Avatar sx={{ bgcolor: "primary.main", mb: 2 }}>
              <LockIcon />
            </Avatar>
            <Typography component="h1" variant="h4" fontWeight="bold">
              Task Dashboard
            </Typography>
            <Typography
              variant="body2"
              color="text.secondary"
              textAlign="center"
            >
              Sign in to manage your tasks and projects
            </Typography>
          </Box>

          {/* Error Alert */}
          {errorMessage && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {errorMessage}
            </Alert>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit(handleFormSubmit)}>
            {/* Email Field */}
            <Controller
              name="email"
              control={control}
              rules={emailValidation}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Email Address"
                  type="email"
                  autoComplete="email"
                  autoFocus
                  margin="normal"
                  error={!!errors.email}
                  helperText={errors.email?.message}
                  disabled={isFormLoading}
                  onChange={(e) => {
                    field.onChange(e);
                    handleClearError();
                  }}
                />
              )}
            />

            {/* Password Field */}
            <Controller
              name="password"
              control={control}
              rules={passwordValidation}
              render={({ field }) => (
                <TextField
                  {...field}
                  fullWidth
                  label="Password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  margin="normal"
                  error={!!errors.password}
                  helperText={errors.password?.message}
                  disabled={isFormLoading}
                  onChange={(e) => {
                    field.onChange(e);
                    handleClearError();
                  }}
                  InputProps={{
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={handleTogglePasswordVisibility}
                          edge="end"
                          disabled={isFormLoading}
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              )}
            />

            {/* Submit Button */}
            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isFormLoading}
              sx={{ mt: 3, mb: 2, py: 1.5 }}
            >
              {isFormLoading ? "Signing In..." : "Sign In"}
            </Button>
          </form>

          <Divider sx={{ my: 3 }} />

          {/* Demo Credentials Section */}
          <Box textAlign="center">
            <Typography variant="body2" color="text.secondary">
              Demo credentials:
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              <strong>Email:</strong> demo@taskdashboard.com
              <br />
              <strong>Password:</strong> demo123
            </Typography>
          </Box>

          {/* Forgot Password Link */}
          <Box textAlign="center" mt={2}>
            <Link href="#" variant="body2" color="primary">
              Forgot password?
            </Link>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginForm;
