import React from "react";

const StatisticCard = ({
  title,
  value,
  trend,
  icon: Icon,
  color = "brand",
}) => {
  const colorMaps = {
    brand: {
      card:
        "from-emerald-950/40 via-slate-900/80 to-slate-950/90 border-emerald-900/40",
      icon:
        "bg-emerald-500/15 border border-emerald-500/25",
      iconColor: "#34d399",
      accent: "#22c55e",
    },

    blue: {
      card:
        "from-blue-950/40 via-slate-900/80 to-slate-950/90 border-blue-900/40",
      icon:
        "bg-blue-500/15 border border-blue-500/25",
      iconColor: "#60a5fa",
      accent: "#3b82f6",
    },

    yellow: {
      card:
        "from-yellow-950/35 via-slate-900/80 to-slate-950/90 border-yellow-900/40",
      icon:
        "bg-yellow-500/15 border border-yellow-500/25",
      iconColor: "#facc15",
      accent: "#eab308",
    },

    brown: {
      card:
        "from-amber-950/40 via-slate-900/80 to-slate-950/90 border-amber-900/40",
      icon:
        "bg-orange-500/15 border border-orange-500/25",
      iconColor: "#fb923c",
      accent: "#f59e0b",
    },

    gray: {
      card:
        "from-slate-800/50 via-slate-900/80 to-slate-950/90 border-slate-700/60",
      icon:
        "bg-slate-500/15 border border-slate-600/40",
      iconColor: "#94a3b8",
      accent: "#94a3b8",
    },

    accent: {
      card:
        "from-cyan-950/40 via-slate-900/80 to-slate-950/90 border-cyan-900/40",
      icon:
        "bg-cyan-500/15 border border-cyan-500/25",
      iconColor: "#2dd4bf",
      accent: "#14b8a6",
    },
  };

  const style = colorMaps[color] || colorMaps.brand;

  const isNegative =
    trend &&
    (trend.includes("-") ||
      trend.includes("decrease") ||
      trend.includes("down"));

  const trendColorClass = isNegative
    ? "text-red-400 bg-red-500/10 border-red-500/25"
    : "text-emerald-400 bg-emerald-500/10 border-emerald-500/25";

  return (
    <div
      className={`
        relative overflow-hidden
        p-5
        rounded-2xl
        border
        bg-gradient-to-br
        ${style.card}
        shadow-lg
        transition-all
        duration-300
        hover:-translate-y-1
        hover:shadow-2xl
        group
        h-[145px]
        flex
        flex-col
        justify-between
      `}
      style={{
        boxShadow: `0 10px 30px rgba(0,0,0,0.18)`,
      }}
    >
      {/* Subtle accent glow */}
      <div
        className="absolute -top-10 -right-10 w-24 h-24 rounded-full blur-3xl opacity-20 pointer-events-none"
        style={{ backgroundColor: style.accent }}
      />

      {/* Top section */}
      <div className="flex items-start justify-between relative z-10">
        <span
          className="text-[10px] font-bold uppercase tracking-widest tech-mono"
          style={{ color: "#94a3b8" }}
        >
          {title}
        </span>

        {Icon && (
          <div
            className={`
              w-12 h-12
              rounded-xl
              ${style.icon}
              flex items-center justify-center
              transition-all duration-300
              group-hover:scale-110
            `}
            style={{
              color: style.iconColor,
              boxShadow: `0 0 20px ${style.accent}18`,
            }}
          >
            <Icon />
          </div>
        )}
      </div>

      {/* Value */}
      <div className="relative z-10 mt-2">
        <h3
          className="text-2xl sm:text-3xl font-extrabold tracking-tight tech-mono"
          style={{
            color: "#f8fafc",
            textShadow: "0 2px 12px rgba(0,0,0,0.35)",
          }}
        >
          {value}
        </h3>

        {trend && (
          <div className="mt-2 flex">
            <span
              className={`
                px-2 py-0.5
                rounded-md
                text-[9px]
                font-bold
                uppercase
                tracking-wider
                border
                ${trendColorClass}
                tech-mono
              `}
            >
              {trend}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatisticCard;
