import React, { useCallback } from "react";
import Head from "next/head";
import { useRouter } from "next/router";
import LoginForm from "../components/LoginForm";

interface UserCredentials {
  email: string;
  password: string;
}

interface UserData {
  name: string;
  email: string;
  role: string;
}

const LoginPage: React.FC = () => {
  const router = useRouter();

  // Handle user login with authentication simulation
  const handleUserLogin = useCallback(
    async (credentials: UserCredentials): Promise<void> => {
      // Simulate authentication API call
      return new Promise<void>((resolve, reject) => {
        // Add artificial delay to simulate network request
        const authenticationDelay = 1000;

        setTimeout(() => {
          // Check demo credentials
          const isValidUser =
            credentials.email === "demo@taskdashboard.com" &&
            credentials.password === "demo123";

          if (isValidUser) {
            // Create user session data
            const userData: UserData = {
              name: "John Doe",
              email: credentials.email,
              role: "developer",
            };

            // Store authentication state
            localStorage.setItem("isAuthenticated", "true");
            localStorage.setItem("user", JSON.stringify(userData));

            // Redirect to dashboard
            router.push("/");
            resolve();
          } else {
            // Authentication failed
            const errorMessage = "Invalid email or password";
            reject(new Error(errorMessage));
          }
        }, authenticationDelay);
      });
    },
    [router]
  );

  return (
    <>
      <Head>
        <title>Login - Task Dashboard</title>
        <meta
          name="description"
          content="Sign in to your task dashboard to manage projects and collaborate with your team"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <LoginForm onLogin={handleUserLogin} />
    </>
  );
};

export default LoginPage;
