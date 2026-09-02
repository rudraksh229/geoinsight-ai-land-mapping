import React from 'react';

export const StatsSkeleton = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4 w-full">
      {[...Array(6)].map((_, i) => (
        <div key={i} className="p-6 rounded-2xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900/50 shadow-xs animate-pulse flex flex-col justify-between h-[140px]">
          <div className="flex items-center justify-between">
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-sm w-20" />
            <div className="w-9 h-9 bg-slate-200 dark:bg-slate-850 rounded-xl" />
          </div>
          <div>
            <div className="h-7 bg-slate-200 dark:bg-slate-800 rounded-md w-28 mb-2" />
            <div className="h-3 bg-slate-200 dark:bg-slate-850 rounded-sm w-24" />
          </div>
        </div>
      ))}
    </div>
  );
};

export const ChartSkeleton = ({ className = '' }) => {
  return (
    <div className={`p-6 bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 rounded-2xl shadow-xs animate-pulse flex flex-col ${className}`}>
      <div className="mb-4">
        <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded-sm w-36 mb-2" />
        <div className="h-3 bg-slate-200 dark:bg-slate-850 rounded-sm w-56" />
      </div>
      <div className="flex-1 flex items-center justify-center min-h-[250px]">
        {/* Pulsing circular or rectangular area */}
        <div className="w-48 h-48 rounded-full border-12 border-slate-100 dark:border-slate-800 flex items-center justify-center">
          <div className="w-24 h-24 bg-slate-100 dark:bg-slate-850 rounded-full" />
        </div>
      </div>
    </div>
  );
};

export const TableSkeleton = () => {
  return (
    <div className="bg-white dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800 rounded-2xl p-6 shadow-xs animate-pulse w-full">
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded-sm w-44 mb-2" />
          <div className="h-3 bg-slate-200 dark:bg-slate-850 rounded-sm w-64" />
        </div>
        <div className="w-20 h-4 bg-slate-200 dark:bg-slate-800 rounded-sm" />
      </div>
      <div className="space-y-4">
        <div className="h-7 bg-slate-100 dark:bg-slate-850 rounded-md w-full" />
        {[...Array(5)].map((_, i) => (
          <div key={i} className="flex gap-4 py-3 border-b border-slate-50 dark:border-slate-800 last:border-0 items-center justify-between">
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-sm w-24" />
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-sm w-24" />
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-sm w-32" />
            <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-sm w-20" />
            <div className="h-5 bg-slate-200 dark:bg-slate-800 rounded-full w-16" />
          </div>
        ))}
      </div>
    </div>
  );
};
