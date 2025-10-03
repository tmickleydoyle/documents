import React from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import LoginForm from "../components/LoginForm";

interface LoginCredentials {
  email: string;
  password: string;
}

const LoginPage: React.FC = () => {
  const router = useRouter();

  const handleLogin = async (credentials: LoginCredentials) => {
    // Simulate API call
    return new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        if (
          credentials.email === "demo@taskdashboard.com" &&
          credentials.password === "demo123"
        ) {
          // Simulate successful login
          localStorage.setItem("isAuthenticated", "true");
          localStorage.setItem(
            "user",
            JSON.stringify({
              name: "John Doe",
              email: credentials.email,
              role: "developer",
            })
          );
          router.push("/");
          resolve();
        } else {
          reject(new Error("Invalid email or password"));
        }
      }, 1000);
    });
  };

  return (
    <>
      <Head>
        <title>Login - Task Dashboard</title>
        <meta name="description" content="Sign in to your task dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <LoginForm onLogin={handleLogin} />
    </>
  );
};

export default LoginPage;
