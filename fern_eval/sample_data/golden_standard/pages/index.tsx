import React from 'react';
import Head from 'next/head';
import { Container, Typography, Button, Box } from '@mui/material';
import { useRouter } from 'next/router';

const HomePage: React.FC = () => {
  const router = useRouter();
  
  const handleGetStarted = () => {
    router.push('/login');
  };
  
  return (
    <>
      <Head>
        <title>Welcome to Our App</title>
        <meta name="description" content="The best Next.js application" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            textAlign: 'center',
          }}
        >
          <Typography variant="h2" component="h1" gutterBottom>
            Welcome to Our Amazing App
          </Typography>
          
          <Typography variant="h5" component="h2" gutterBottom color="text.secondary">
            Build faster, deploy smarter, grow better
          </Typography>
          
          <Typography variant="body1" sx={{ mb: 4, maxWidth: 600 }}>
            Experience the next generation of web applications with our cutting-edge
            technology stack. Built with Next.js, React, and modern best practices.
          </Typography>
          
          <Button
            variant="contained"
            size="large"
            onClick={handleGetStarted}
            sx={{ mt: 2, px: 4, py: 1.5 }}
          >
            Get Started
          </Button>
        </Box>
      </Container>
    </>
  );
};

export default HomePage;