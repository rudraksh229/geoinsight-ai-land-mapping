import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';

const Navbar = ({ onMenuToggle, isSidebarCollapsed }) => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const notifications = [
    { id: 1, text: 'Analysis report REP-2026-008 completed.', time: '5m ago', read: false },
    { id: 2, text: 'AI Model v2.4 classification weights updated.', time: '1h ago', read: true },
    { id: 3, text: 'Backup of Geoportal datasets completed.', time: '1d ago', read: true }
  ];

  const handleLogout = () => {
    logout();
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-white/85 dark:bg-slate-900/85 backdrop-blur-md border-b border-slate-150 dark:border-slate-800/60 transition-colors duration-300">
      <div className="flex h-16 items-center justify-between px-4 sm:px-6">

        {/* Left section: Logo and Mobile Menu toggle */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuToggle}
            className="p-2 -ml-2 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 md:hidden cursor-pointer"
            aria-label="Toggle Menu"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.2}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
              />
            </svg>
          </button>

          <div className="flex items-center gap-2.5">

            {/* Mobile branding */}
            <div className="p-2 rounded-xl bg-green-600 text-white flex items-center justify-center shadow-xs md:hidden">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2.2}
                stroke="currentColor"
                className="w-5 h-5"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z"
                />
              </svg>
            </div>

            <div className="md:hidden">
              <h1 className="text-sm font-extrabold text-slate-800 dark:text-slate-100 tracking-tight leading-tight m-0">
                AI Land Mapping
              </h1>

              <p className="text-[9px] text-green-600 dark:text-green-400 font-bold uppercase tracking-wider leading-none mt-0.5">
                NRSC Geoportal
              </p>
            </div>

            {/* Desktop page title */}
            <div className="hidden md:block">

              <span
                className="text-[10px] font-bold uppercase tracking-widest block leading-none"
                style={{
                  textShadow: '0 0 4px rgba(255,255,255,0.18)'
                }}
              >
                GeoInsight AI
              </span>

              <span
                className="text-sm font-bold mt-1 block"
                style={{
                  textShadow: '0 0 5px rgba(255,255,255,0.15)'
                }}
              >
                Administrative Dashboard
              </span>

            </div>
          </div>
        </div>

        {/* Right section: System Status, Notifications & Profile */}
        <div className="flex items-center gap-3 sm:gap-4">

          {/* Status Indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800/40 transition-colors">
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
            </span>

            <span className="text-[10px] font-bold text-green-700 dark:text-green-400 tracking-wider uppercase">
              AI Server: Online
            </span>
          </div>

          {/* Notifications Trigger */}
          <div className="relative">
            <button
              onClick={() => {
                setShowNotifications(!showNotifications);
                setShowProfileMenu(false);
              }}
              className={`p-2 rounded-xl border text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-all ${showNotifications
                ? 'bg-slate-50 dark:bg-slate-800 border-slate-350 dark:border-slate-600'
                : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-700'
                }`}
            >
              <span className="relative block">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2.2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0"
                  />
                </svg>

                <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-red-500 border border-white dark:border-slate-900" />
              </span>
            </button>

            {/* Notifications Menu */}
            {showNotifications && (
              <div className="absolute right-0 mt-2.5 w-72 bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 rounded-2xl shadow-xl py-2 z-50 animate-slide-in">

                <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
                  <h4 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider">
                    Alerts & Notifications
                  </h4>

                  <span className="px-1.5 py-0.5 rounded-sm bg-red-50 dark:bg-red-950/30 text-[10px] font-bold text-red-650 dark:text-red-400">
                    New
                  </span>
                </div>

                <div className="max-h-60 overflow-y-auto">
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className={`px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 border-b border-slate-50 dark:border-slate-800 last:border-0 cursor-pointer flex gap-3 ${!notif.read ? 'bg-green-50/20 dark:bg-green-950/5' : ''
                        }`}
                    >
                      <span
                        className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${!notif.read ? 'bg-green-600' : 'bg-transparent'
                          }`}
                      />

                      <div>
                        <p className="text-xs font-semibold text-slate-700 dark:text-slate-300 leading-normal">
                          {notif.text}
                        </p>

                        <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium block mt-1">
                          {notif.time}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Profile Menu Trigger */}
          <div className="relative">
            <button
              onClick={() => {
                setShowProfileMenu(!showProfileMenu);
                setShowNotifications(false);
              }}
              className="flex items-center gap-2 p-1.5 rounded-full border border-slate-200 dark:border-slate-700 hover:border-slate-350 dark:hover:border-slate-500 bg-white dark:bg-slate-900 cursor-pointer transition-all"
            >
              <div className="w-8 h-8 rounded-full bg-green-705 bg-gradient-to-tr from-green-700 to-emerald-600 text-white font-extrabold text-xs flex items-center justify-center uppercase shadow-xs">
                {user?.name
                  ? user.name
                    .split(' ')
                    .map(n => n[0])
                    .join('')
                    .substring(0, 2)
                  : 'NR'}
              </div>
            </button>

            {/* Profile Dropdown */}
            {showProfileMenu && (
              <div className="absolute right-0 mt-2.5 w-56 bg-white dark:bg-slate-900 border border-slate-150 dark:border-slate-800 rounded-2xl shadow-xl py-2.5 z-50 animate-slide-in">

                <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-800 mb-1">
                  <p className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate leading-normal">
                    {user?.name || 'GIS Officer'}
                  </p>

                  <p className="text-[10px] text-slate-450 dark:text-slate-500 font-semibold truncate leading-none mt-1">
                    {user?.email || 'officer@gov.in'}
                  </p>
                </div>

                <div className="px-2">

                  <a
                    href="#/profile"
                    onClick={() => setShowProfileMenu(false)}
                    className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-650 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-205 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2.2}
                      stroke="currentColor"
                      className="w-4 h-4"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z"
                      />
                    </svg>

                    My Profile
                  </a>

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 transition-colors cursor-pointer"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                      strokeWidth={2.2}
                      stroke="currentColor"
                      className="w-4 h-4"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75"
                      />
                    </svg>

                    Sign Out
                  </button>

                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </header>
  );
};

export default Navbar;
