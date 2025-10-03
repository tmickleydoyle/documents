import React from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import LoginComponent from "../components/LoginComponent";

interface LoginCredentials {
  email: string;
  password: string;
}

const LoginPage = () => {
  const router = useRouter();

  const handleLogin = async (credentials: LoginCredentials) => {
    return new Promise<void>((resolve, reject) => {
      setTimeout(() => {
        // Simple auth check
        if (
          credentials.email === "demo@taskdashboard.com" &&
          credentials.password === "demo123"
        ) {
          // Store auth data
          localStorage.setItem("authenticated", "true");
          localStorage.setItem(
            "currentUser",
            JSON.stringify({
              name: "John Doe",
              email: credentials.email,
              role: "developer",
            })
          );
          router.push("/");
          resolve();
        } else {
          reject(new Error("Invalid login credentials"));
        }
      }, 1200); // Longer delay to simulate AI-generated code
    });
  };

  return (
    <>
      <Head>
        <title>Login - Task Manager</title>
        <meta name="description" content="Login to task manager" />
      </Head>

      <LoginComponent onLogin={handleLogin} />
    </>
  );
};

export default LoginPage;
