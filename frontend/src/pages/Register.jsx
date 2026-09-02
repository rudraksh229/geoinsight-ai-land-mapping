import React, { useState } from 'react';
import { useNavigate, Link } from "react-router-dom";
import { register as registerService } from "../services/authService";
import NotificationToast from '../components/NotificationToast';

const Register = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  const showToast = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();

    if (!username || !email || !password) {
        showToast("Please fill in all fields", "error");
        return;
    }

    setIsSubmitting(true);

    try {
        await registerService({
            name: username,
            email,
            password,
        });

        showToast("Registration Successful! Please log in.", "success");

        setTimeout(() => {
            navigate("/login");
        }, 1500);

    } catch (error) {
        console.log(error);
        
        const errorMsg = error.response?.data?.detail || "Registration failed. Please try again.";
        showToast(errorMsg, "error");
    }

    setIsSubmitting(false);
  };

  return (
    <div className="glass-card rounded-3xl p-8 sm:p-10 relative transition-colors duration-300 glow-cyan">
      {/* Decorative scanning widget */}
      <div className="absolute top-0 right-10 -translate-y-1/2 glow-green bg-green-500/20 text-green-400 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest shadow-xs border border-green-500/50 tech-mono">
        Secure Portal
      </div>

      <div className="text-center mb-8">
        <h2 className="text-2xl font-extrabold text-slate-100 tracking-tight leading-tight tech-mono">AI GIS Platform</h2>
        <p className="text-xs font-semibold text-slate-400 mt-1.5 uppercase tracking-wider tech-mono">Create a New Account</p>
      </div>

      <form onSubmit={handleRegisterSubmit} className="space-y-5">
        <div>
          <label htmlFor="username" className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Full Name / Username</label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-450 dark:text-slate-500">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
              </svg>
            </span>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-600 focus:border-green-500 focus:bg-slate-800 rounded-xl text-xs font-bold outline-hidden transition-all text-slate-100 placeholder-slate-500 tech-mono"
              placeholder="Officer Name"
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="email" className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Government Email ID</label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-450 dark:text-slate-500">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
            </span>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-600 focus:border-green-500 focus:bg-slate-800 rounded-xl text-xs font-bold outline-hidden transition-all text-slate-100 placeholder-slate-500 tech-mono"
              placeholder="officer.name@gov.in"
              required
            />
          </div>
        </div>

        <div>
          <label htmlFor="password" className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Access PIN / Password</label>
          <div className="relative">
            <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-450 dark:text-slate-500">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
            </span>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-600 focus:border-green-500 focus:bg-slate-800 rounded-xl text-xs font-bold outline-hidden transition-all text-slate-100 placeholder-slate-500 tech-mono"
              placeholder="••••••••"
              required
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full glow-green bg-green-500/20 hover:bg-green-500/30 border border-green-500/50 active:bg-green-500/40 disabled:bg-slate-800 text-green-400 py-3 px-4 rounded-xl font-bold uppercase tracking-wider text-xs transition-all flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed mt-4 tech-mono"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Registering...
            </>
          ) : (
            'Register Account'
          )}
        </button>

        <div className="text-center mt-4 pt-4 border-t border-slate-200 dark:border-slate-800">
          <p className="text-xs text-slate-500 dark:text-slate-400 font-bold">
            Already have an account?{' '}
            <Link to="/login" className="text-green-600 hover:text-green-700 dark:text-green-500 dark:hover:text-green-400 transition-colors">
              Log in here
            </Link>
          </p>
        </div>
      </form>

      {/* Notification Toast */}
      {toastMessage && (
        <NotificationToast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage('')}
        />
      )}
    </div>
  );
};

export default Register;
