import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-100 py-4 px-6 text-center text-xs text-slate-400 font-semibold tracking-wider">
      <div className="flex flex-col sm:flex-row justify-between items-center gap-2 max-w-7xl mx-auto">
        <div>
          © 2026 AI-Based Land Mapping System. National Remote Sensing Centre (NRSC) / ISRO.
        </div>
        <div className="flex items-center gap-3">
          <a href="#/privacy" className="hover:text-slate-600 transition-colors">Privacy Policy</a>
          <span>•</span>
          <a href="#/terms" className="hover:text-slate-600 transition-colors">Terms of Service</a>
          <span>•</span>
          <span className="text-green-600 font-bold uppercase tracking-widest text-[10px]">v1.2.0 Stable</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
