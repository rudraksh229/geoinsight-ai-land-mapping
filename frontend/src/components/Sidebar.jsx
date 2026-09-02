import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar = ({ isOpen, onClose, isCollapsed, onToggleCollapse }) => {
  const navigationItems = [
    {
      name: 'Dashboard',
      path: '/',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 shrink-0">
          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
        </svg>
      )
    },
    {
      name: 'Land Mapping',
      path: '/mapping',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 shrink-0">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.89-1.63c.807-.27 1.357-1.022 1.357-1.88V4.162c0-.959-.88-1.72-1.824-1.498l-4.58 1.077c-.428.101-.874.101-1.302 0l-5.94-1.396a2.25 2.25 0 00-1.034 0L2.162 3.422A1.82 1.82 0 001 5.16v12.3c0 .858.55 1.61 1.357 1.88l4.89 1.63a2.25 2.25 0 001.506 0l5.75-1.916a2.25 2.25 0 011.506 0z" />
        </svg>
      )
    },
    {
      name: 'Reports',
      path: '/reports',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 shrink-0">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        </svg>
      )
    },
    {
      name: 'Profile Settings',
      path: '/profile',
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5 shrink-0">
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.43l-1.003.828c-.293.241-.438.613-.43.992a7.723 7.723 0 010 .255c-.008.378.137.75.43.991l1.004.827c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.94-1.11.94h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.43l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.991l-1.004-.827a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.645-.869l.214-1.28z" />
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      )
    }
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-slate-900 dark:bg-slate-950 border-r border-slate-600 text-white relative transition-all duration-300">
      {/* Brand Header */}
      <div className={`flex h-16 items-center border-b border-slate-600 gap-2.5 transition-all duration-300 ${isCollapsed ? 'justify-center px-2' : 'px-5'
        }`}>
        <div className="p-2 rounded-xl bg-green-600 text-white flex items-center justify-center shadow-md shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.2} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
          </svg>
        </div>
        {!isCollapsed && (
          <div className="animate-[fadeIn_0.2s_ease-out]">
            <span
              className="text-sm font-bold uppercase tracking-widest block leading-none text-white"
              style={{ textShadow: '0 0 4px rgba(255, 255, 255, 1)' }}>GeoInsight AI</span>
            <span className="text-[9px] text-green-500 font-bold uppercase tracking-wider block tech-mono">Land Mapping Platform</span>
          </div>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-2 px-3 py-6">
        {navigationItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            onClick={onClose}
            title={isCollapsed ? item.name : ''}
            className={({ isActive }) =>
              `flex items-center gap-3.5 px-3 py-3 rounded-xl text-[11px] font-bold uppercase tracking-wider tech-mono transition-all duration-200 ${isCollapsed ? 'justify-center' : ''
              } ${isActive
                ? 'glow-green bg-green-500/10 text-green-400 border border-green-500/30 shadow-sm'
                : 'text-slate-300 hover:text-green-300 hover:bg-green-500/10 border border-transparent hover:border-green-500/25 hover:shadow-sm'
              }`
            }
          >
            {item.icon}
            {!isCollapsed && <span className="animate-[fadeIn_0.2s_ease-out]">{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Bottom Info Details */}
      <div className={`border-t border-slate-600 bg-slate-950/40 transition-all ${isCollapsed ? 'p-2 flex justify-center' : 'p-4'
        }`}>
        {isCollapsed ? (
          <div className="w-8 h-8 rounded-lg bg-slate-800/50 flex items-center justify-center text-slate-400" title="NRSC active workspace">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          </div>
        ) : (
          <div className="p-3 bg-slate-800/50 rounded-xl animate-[fadeIn_0.2s_ease-out]">
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">Active Workspace</p>
            <p className="text-xs font-semibold text-slate-200 mt-1 truncate">NRSC National Portal</p>
            <div className="flex items-center gap-1.5 mt-2.5">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[9px] text-green-400 font-bold uppercase tracking-widest">Local Session</span>
            </div>
          </div>
        )}
      </div>

      {/* Desktop Collapse Toggle Button */}
      {onToggleCollapse && (
        <button
          onClick={onToggleCollapse}
          className="hidden md:flex absolute top-1/2 -right-3 -translate-y-1/2 w-6.5 h-6.5 bg-slate-800 border border-slate-700 hover:bg-green-600 rounded-full items-center justify-center text-slate-400 hover:text-white cursor-pointer z-50 shadow-md transition-all duration-300"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={3}
            stroke="currentColor"
            className={`w-3 h-3 transform transition-transform duration-300 ${isCollapsed ? 'rotate-180' : ''}`}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
        </button>
      )}
    </div>
  );

  return (
    <>
      {/* Desktop Sidebar (Permanent) */}
      <aside className={`hidden md:block h-screen sticky top-0 shrink-0 z-30 transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-64'
        }`}>
        {sidebarContent}
      </aside>

      {/* Mobile Drawer (Conditional overlay) */}
      <div
        className={`fixed inset-0 z-50 md:hidden transition-opacity duration-300 ${isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
          }`}
      >
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs"
          onClick={onClose}
        />

        {/* Drawer panel */}
        <div
          className={`fixed inset-y-0 left-0 w-64 bg-slate-900 shadow-2xl transition-transform duration-300 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'
            }`}
        >
          {/* Close button inside mobile menu */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-slate-600">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-white text-sm tech-mono">AI GEOPORTAL</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.2} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="h-[calc(100%-4rem)] overflow-y-auto">
            {sidebarContent}
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
