import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext(null);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // Lock theme to dark for Mission Control aesthetic
  const [theme] = useState('dark');

  useEffect(() => {
    const root = window.document.documentElement;
    const body = window.document.body;
    
    // Always enforce dark mode classes
    root.classList.add('dark');
    body.classList.add('dark');
    localStorage.setItem('gis_theme', 'dark');
  }, []);

  const toggleTheme = () => {
    // Theme toggle disabled for this specific aesthetic
    console.log("Theme toggle disabled in Mission Control theme");
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
