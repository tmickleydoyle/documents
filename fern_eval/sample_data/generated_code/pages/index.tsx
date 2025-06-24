import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Welcome to My App</h1>
        <p>This is a great application built with Next.js</p>
        <Link href="/login">
          <a className="cta-button">Get Started</a>
        </Link>
      </div>
      
      <div className="features">
        <h2>Features</h2>
        <ul>
          <li>Fast and reliable</li>
          <li>Easy to use</li>
          <li>Modern design</li>
        </ul>
      </div>
    </div>
  );
}