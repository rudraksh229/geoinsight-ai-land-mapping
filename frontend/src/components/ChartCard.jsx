import React from "react";

const ChartCard = ({
  title,
  subtitle,
  children,
  className = "",
}) => {
  return (
    <div
      className={`
        p-6
        rounded-2xl
        border
        border-slate-800/80
        bg-gradient-to-br
        from-slate-900/95
        via-slate-900/90
        to-slate-950/95
        shadow-lg
        hover:shadow-xl
        transition-all
        duration-300
        flex
        flex-col
        ${className}
      `}
    >
      {(title || subtitle) && (
        <div className="mb-4">
          {title && (
            <h4
              className="text-base font-bold tracking-tight tech-mono"
              style={{ color: "#f1f5f9" }}
            >
              {title}
            </h4>
          )}

          {subtitle && (
            <p
              className="text-xs mt-1 font-semibold leading-normal tech-mono"
              style={{ color: "#94a3b8" }}
            >
              {subtitle}
            </p>
          )}
        </div>
      )}

      <div className="flex-1 flex items-center justify-center min-h-[250px] relative">
        {children}
      </div>
    </div>
  );
};

export default ChartCard;
