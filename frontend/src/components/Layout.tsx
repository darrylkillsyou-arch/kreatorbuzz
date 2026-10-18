import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Footer } from './Footer';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-background font-body-md text-body-md text-on-surface antialiased">
      <Navbar />
      <main className="w-full pt-20 bg-background flex-grow">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};
