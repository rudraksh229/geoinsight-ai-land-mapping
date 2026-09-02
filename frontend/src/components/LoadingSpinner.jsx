import React from 'react';

const LoadingSpinner = ({
  message = 'Loading...',
  fullScreen = false,
  size = 'md',
}) => {
  const spinnerSizes = {
    sm: 'w-6 h-6 border-2',
    md: 'w-10 h-10 border-3',
    lg: 'w-16 h-16 border-4',
  };

  const selectedSize = spinnerSizes[size] || spinnerSizes.md;

  const spinnerContent = (
    <div className="flex flex-col items-center justify-center gap-5 text-center p-6">
      <div className="relative">
        {/* Outer glowing ring */}
        <div
          className={`rounded-full border-solid border-green-300 ${selectedSize}`}
        />

        {/* Inner rotating core */}
        <div
          className={`absolute inset-0 rounded-full border-4 border-transparent border-t-green-400 border-r-green-400 animate-spin ${selectedSize}`}
        />
      </div>

      {message && (
        <div className="bg-slate-950 rounded-xl px-5 py-3 border border-green-500/40 shadow-lg">
          <p className="text-sm font-bold text-white tracking-wide leading-relaxed">
            {message}
          </p>
        </div>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm">
        <div className="bg-slate-900 p-8 rounded-2xl shadow-xl max-w-md border border-slate-700 flex flex-col items-center">
          {spinnerContent}
        </div>
      </div>
    );
  }

  return spinnerContent;
};

export default LoadingSpinner;
