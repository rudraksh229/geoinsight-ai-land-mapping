import React from 'react';

const AuthLayout = ({ children }) => {
  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{
        backgroundImage: `
          radial-gradient(circle at 20% 30%, rgba(34, 197, 94, 0.12) 0%, transparent 50%),
          radial-gradient(circle at 80% 70%, rgba(56, 189, 248, 0.10) 0%, transparent 50%)
        `
      }}
    >
      {/* Dynamic scan line effect */}
      <div className="absolute inset-0 bg-linear-to-b from-transparent via-green-500/5 to-transparent h-[150%] animate-[pulse_6s_infinite] pointer-events-none" />
      <div className="w-full max-w-md relative z-10">
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;
