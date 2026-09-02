import React, { useState, useEffect } from "react";

import {
  getDashboardStats,
  getDashboardCharts,
  getRecentReports,
} from "../services/dashboardService";

import { useTheme } from "../context/ThemeContext";
import StatisticCard from "../components/StatisticCard";
import ChartCard from "../components/ChartCard";
import SearchBar from "../components/SearchBar";

import {
  StatsSkeleton,
  ChartSkeleton,
  TableSkeleton,
} from "../components/SkeletonLoaders";

import NotificationToast from "../components/NotificationToast";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { Pie, Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);


// ============================================
// DASHBOARD
// ============================================

const Dashboard = () => {
  const { theme } = useTheme();

  // ==========================================
  // STATE
  // ==========================================

  const [loading, setLoading] = useState(true);

  const [stats, setStats] = useState(null);

  const [charts, setCharts] = useState(null);

  const [recentAnalyses, setRecentAnalyses] = useState([]);

  const [allAnalyses, setAllAnalyses] = useState([]);

  const [searchQuery, setSearchQuery] = useState("");

  const [toastMessage, setToastMessage] = useState("");

  const [toastType, setToastType] = useState("success");


  // ==========================================
  // TOAST
  // ==========================================

  const showToast = (message, type = "success") => {
    setToastMessage(message);
    setToastType(type);
  };


  // ==========================================
  // FETCH DASHBOARD DATA
  // ==========================================

  const fetchDashboardData = async () => {
    setLoading(true);

    try {
      const [
        statsData,
        chartsData,
        recentData,
      ] = await Promise.all([
        getDashboardStats(),
        getDashboardCharts(),
        getRecentReports(),
      ]);

      console.log("Dashboard Stats:", statsData);
      console.log("Dashboard Charts:", chartsData);
      console.log("Recent Reports:", recentData);

      setStats(statsData);
      setCharts(chartsData);

      const reports =
        Array.isArray(recentData)
          ? recentData
          : [];

      setAllAnalyses(reports);
      setRecentAnalyses(reports);

    } catch (error) {
      console.error(
        "Dashboard loading error:",
        error
      );

      showToast(
        "Failed to retrieve dashboard records.",
        "error"
      );

    } finally {
      setLoading(false);
    }
  };


  // ==========================================
  // INITIAL LOAD
  // ==========================================

  useEffect(() => {
    fetchDashboardData();
  }, []);


  // ==========================================
  // SEARCH
  // ==========================================

  const handleSearch = (query) => {
    setSearchQuery(query);

    if (!query.trim()) {
      setRecentAnalyses(allAnalyses);
      return;
    }

    const search = query.toLowerCase();

    const filtered =
      allAnalyses.filter((item) => {
        const village =
          String(
            item.village || ""
          ).toLowerCase();

        const district =
          String(
            item.district || ""
          ).toLowerCase();

        const state =
          String(
            item.state || ""
          ).toLowerCase();

        const status =
          String(
            item.status || ""
          ).toLowerCase();

        return (
          village.includes(search) ||
          district.includes(search) ||
          state.includes(search) ||
          status.includes(search)
        );
      });

    setRecentAnalyses(filtered);
  };


  // ==========================================
  // DATA CHECK
  // ==========================================

  const hasAnalysisData =
    stats?.hasData === true &&
    charts?.hasData === true;


  // ==========================================
  // PIE CHART
  // ==========================================

  const pieData =
    hasAnalysisData &&
      charts?.pieChart?.labels?.length > 0
      ? {
        labels:
          charts.pieChart.labels,

        datasets: [
          {
            data:
              charts.pieChart.data || [],

            backgroundColor: [
              "#22c55e",
              "#34d399",
              "#f59e0b",
              "#64748b",
              "#38bdf8",
            ],

            borderWidth:
              theme === "dark"
                ? 2
                : 1,

            borderColor:
              theme === "dark"
                ? "#0f172a"
                : "#ffffff",
          },
        ],
      }
      : null;


  // ==========================================
  // BAR CHART
  // ==========================================

  const barData =
    hasAnalysisData &&
      charts?.barChart?.labels?.length > 0
      ? {
        labels:
          charts.barChart.labels || [],

        datasets: [
          {
            label: "Vegetation",

            data:
              charts.barChart.vegetation || [],

            backgroundColor: "#22c55e",

            borderRadius: 6,

            borderSkipped: false,
          },

          {
            label: "Agricultural Land",

            data:
              charts.barChart.agriculture || [],

            backgroundColor: "#34d399",

            borderRadius: 6,

            borderSkipped: false,
          },

          {
            label: "Barren Land",

            data:
              charts.barChart.barren || [],

            backgroundColor: "#f59e0b",

            borderRadius: 6,

            borderSkipped: false,
          },

          {
            label: "Urban Land",

            data:
              charts.barChart.urban || [],

            backgroundColor: "#64748b",

            borderRadius: 6,

            borderSkipped: false,
          },

          {
            label: "Water Bodies",

            data:
              charts.barChart.water || [],

            backgroundColor: "#38bdf8",

            borderRadius: 6,

            borderSkipped: false,
          },
        ],
      }
      : null;


  // ==========================================
  // THEME COLORS
  // ==========================================

  const isDark =
    theme === "dark";

  const textColor =
    isDark
      ? "#cbd5e1"
      : "#475569";

  const gridColor =
    isDark
      ? "#1e293b"
      : "#e2e8f0";


  // ==========================================
  // PIE / COMMON CHART OPTIONS
  // ==========================================

  const chartOptions = {
    responsive: true,

    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: "bottom",

        labels: {
          boxWidth: 8,

          color: textColor,

          font: {
            size: 9,
            weight: "bold",
          },

          padding: 12,
        },
      },

      tooltip: {
        backgroundColor:
          isDark
            ? "#020617"
            : "#ffffff",

        titleColor:
          isDark
            ? "#f8fafc"
            : "#0f172a",

        bodyColor:
          isDark
            ? "#cbd5e1"
            : "#334155",

        borderColor:
          isDark
            ? "#334155"
            : "#e2e8f0",

        borderWidth: 1,

        padding: 10,

        cornerRadius: 8,
      },
    },
  };


  // ==========================================
  // BAR CHART OPTIONS
  // ==========================================

  const barChartOptions = {
    ...chartOptions,

    scales: {
      x: {
        grid: {
          display: false,
        },

        ticks: {
          color: textColor,

          font: {
            size: 9,
            weight: "bold",
          },
        },
      },

      y: {
        beginAtZero: true,

        grid: {
          color: gridColor,
        },

        ticks: {
          color: textColor,

          font: {
            size: 9,
          },
        },

        title: {
          display: true,

          text: "Area (Ha)",

          color: textColor,

          font: {
            size: 9,
            weight: "bold",
          },
        },
      },
    },
  };


  // ==========================================
  // STATUS LABEL
  // ==========================================

  const getStatusLabel = (status) => {
    const value =
      String(status || "")
        .trim()
        .toLowerCase();

    switch (value) {
      case "1":
        return "Vegetation";

      case "2":
        return "Agriculture";

      case "3":
        return "Built-up";

      case "4":
        return "Barren";

      case "5":
        return "Water";

      case "vegetation":
        return "Vegetation";

      case "agriculture":
        return "Agriculture";

      case "built-up":
      case "builtup":
      case "built up":
        return "Built-up";

      case "barren":
        return "Barren";

      case "water":
        return "Water";

      case "completed":
        return "Completed";

      default:
        return status || "Completed";
    }
  };


  // ==========================================
  // STATUS CLASS
  // ==========================================

  const getStatusClass = (status) => {
    const label =
      getStatusLabel(status);

    switch (label) {
      case "Vegetation":
        return `
          bg-green-500/10
          border-green-500/25
          text-green-400
        `;

      case "Agriculture":
        return `
          bg-yellow-500/10
          border-yellow-500/25
          text-yellow-400
        `;

      case "Barren":
        return `
          bg-amber-500/10
          border-amber-500/25
          text-amber-400
        `;

      case "Water":
        return `
          bg-blue-500/10
          border-blue-500/25
          text-blue-400
        `;

      case "Built-up":
        return `
          bg-slate-500/10
          border-slate-600/40
          text-slate-300
        `;

      default:
        return `
          bg-emerald-500/10
          border-emerald-500/25
          text-emerald-400
        `;
    }
  };


  // ==========================================
  // ICONS
  // ==========================================

  // TOTAL ANALYSED — Globe
  const AreaIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.8}
      stroke="currentColor"
      className="w-7 h-7"
    >
      <circle
        cx="12"
        cy="12"
        r="9"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 12h18"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3c2.5 2.4 3.8 5.4 3.8 9s-1.3 6.6-3.8 9"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3c-2.5 2.4-3.8 5.4-3.8 9s1.3 6.6 3.8 9"
      />
    </svg>
  );


  // VEGETATION — Leaf
  const VegIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.8}
      stroke="currentColor"
      className="w-7 h-7"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M20.5 3.5C12 3.5 5 7 5 13.5A6.5 6.5 0 0011.5 20C18 20 20.5 11.5 20.5 3.5z"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M5 19.5c3.2-4.8 6.4-7.8 11-10.5"
      />
    </svg>
  );


  // AGRICULTURE — Field / Crop
  const AgriIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.8}
      stroke="currentColor"
      className="w-7 h-7"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 19h18"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M5 16c2-2 4-3 7-3s5 1 7 3"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M6 16l2-5"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10 16l2-6"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M14 16l2-5"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M18 16l1-3"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 4v6"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9.5 6.5h5"
      />
    </svg>
  );


  // BARREN LAND — Dry tree / land
  const BarrenIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.8}
      stroke="currentColor"
      className="w-7 h-7"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 20V8"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 10L8 6"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 13l5-5"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M8 6V3"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M17 8V5"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M7 20c2-1 8-1 10 0"
      />
    </svg>
  );


  // WATER — Droplet
  const WaterIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.8}
      stroke="currentColor"
      className="w-7 h-7"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 3s6 6.2 6 11a6 6 0 11-12 0c0-4.8 6-11 6-11z"
      />

      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 16.5c.7 1 1.6 1.5 3 1.5"
      />
    </svg>
  );


  // AI ACCURACY — Target
  const AccuracyIcon = () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.8}
      stroke="currentColor"
      className="w-7 h-7"
    >
      <circle
        cx="12"
        cy="12"
        r="8"
      />

      <circle
        cx="12"
        cy="12"
        r="4"
      />

      <circle
        cx="12"
        cy="12"
        r="1"
        fill="currentColor"
      />

      <path
        strokeLinecap="round"
        d="M12 2v2"
      />

      <path
        strokeLinecap="round"
        d="M12 20v2"
      />

      <path
        strokeLinecap="round"
        d="M2 12h2"
      />

      <path
        strokeLinecap="round"
        d="M20 12h2"
      />
    </svg>
  );


  // ==========================================
  // LOADING STATE
  // ==========================================

  if (loading) {
    return (
      <div className="space-y-6 w-full animate-pulse">

        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

          <div>
            <div className="h-6 bg-slate-800 rounded-md w-48 mb-2" />

            <div className="h-3.5 bg-slate-800 rounded-sm w-72" />
          </div>

          <div className="w-48 h-10 bg-slate-800 rounded-xl" />

        </div>

        <StatsSkeleton />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

          <ChartSkeleton className="lg:col-span-1" />

          <ChartSkeleton className="lg:col-span-2" />

        </div>

        <TableSkeleton />

      </div>
    );
  }


  // ==========================================
  // MAIN DASHBOARD
  // ==========================================

  return (
    <div className="space-y-6">

      {/* ========================================
          HEADER
      ======================================== */}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">

        <div>

          <h2
            className="text-xl font-extrabold tracking-tight"
            style={{
              color: "#f8fafc",
              textShadow: "0 2px 10px rgba(0,0,0,0.25)",
            }}
          >
            GIS Operational Analytics
          </h2>

          <p
            className="text-xs font-bold mt-1 uppercase tracking-wider"
            style={{ color: "#94a3b8" }}
          >
            Overview of land cover classifications across monitoring sites
          </p>

        </div>

        <div className="flex items-center gap-2">

          <SearchBar
            placeholder="Search village analyses..."
            value={searchQuery}
            onChange={handleSearch}
          />

          <a
            href="#/mapping"
            className="
              px-4
              py-2.5
              bg-green-600
              hover:bg-green-500
              text-white
              rounded-xl
              font-bold
              uppercase
              tracking-wider
              text-[10px]
              shadow-sm
              hover:shadow-lg
              transition-all
              cursor-pointer
              flex
              items-center
              gap-1.5
              shrink-0
            "
          >

            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2.5}
              stroke="currentColor"
              className="w-4 h-4"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 4.5v15m7.5-7.5h-15"
              />
            </svg>

            Analyze Area

          </a>

        </div>

      </div>


      {/* ========================================
          NO DATA STATE
      ======================================== */}

      {!hasAnalysisData ? (

        <div className="glass-card rounded-2xl p-10">

          <div className="max-w-md mx-auto text-center">

            <div className="w-16 h-16 mx-auto rounded-2xl bg-green-500/10 text-green-400 flex items-center justify-center mb-5">

              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.8}
                stroke="currentColor"
                className="w-8 h-8"
              >

                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M3.75 3.75h16.5v16.5H3.75z"
                />

                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M7.5 15.75l3-3 2.25 2.25 3.75-4.5"
                />

              </svg>

            </div>

            <h3
              className="text-lg font-extrabold"
              style={{ color: "#f1f5f9" }}
            >
              No Analysis Data Available
            </h3>

            <p
              className="text-sm mt-2 leading-relaxed"
              style={{ color: "#94a3b8" }}
            >
              No land area has been analyzed yet. Start a new satellite
              imagery analysis to populate the dashboard with real GIS data.
            </p>

            <a
              href="#/mapping"
              className="inline-flex items-center gap-2 mt-6 px-5 py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-bold text-xs uppercase tracking-wider transition-all shadow-md"
            >
              Start Land Analysis

              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
                className="w-4 h-4"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.5 4.5L19.5 10.5L13.5 16.5M19.5 10.5H4.5"
                />
              </svg>

            </a>

          </div>

        </div>

      ) : (

        <>

          {/* ========================================
              STATISTIC CARDS
          ======================================== */}

          {stats && (

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-4">

              <StatisticCard
                title="Total Analysed"
                value={stats.totalArea}
                trend={null}
                icon={AreaIcon}
                color="blue"
              />

              <StatisticCard
                title="Vegetation"
                value={stats.vegetation}
                trend={null}
                icon={VegIcon}
                color="brand"
              />

              <StatisticCard
                title="Agriculture"
                value={stats.agriculturalLand}
                trend={null}
                icon={AgriIcon}
                color="yellow"
              />

              <StatisticCard
                title="Barren Land"
                value={stats.barrenLand}
                trend={null}
                icon={BarrenIcon}
                color="brown"
              />

              <StatisticCard
                title="Water Bodies"
                value={stats.waterBodies}
                trend={null}
                icon={WaterIcon}
                color="accent"
              />

              <StatisticCard
                title="AI Accuracy"
                value={stats.aiConfidence}
                trend={null}
                icon={AccuracyIcon}
                color="gray"
              />

            </div>
          )}


          {/* ========================================
              CHARTS
          ======================================== */}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* PIE CHART */}

            <ChartCard
              title="Overall Land Distribution"
              subtitle="Distribution based on completed analyses"
              className="lg:col-span-1"
            >

              {pieData ? (

                <div className="w-full h-64 flex items-center justify-center">

                  <Pie
                    data={pieData}
                    options={chartOptions}
                  />

                </div>

              ) : (

                <div
                  className="h-64 flex items-center justify-center text-sm"
                  style={{ color: "#94a3b8" }}
                >
                  No classification data available
                </div>

              )}

            </ChartCard>


            {/* BAR CHART */}

            <ChartCard
              title="Land Cover Metrics"
              subtitle="Mapped area by land classification"
              className="lg:col-span-2"
            >

              {barData ? (

                <div className="w-full h-64">

                  <Bar
                    data={barData}
                    options={barChartOptions}
                  />

                </div>

              ) : (

                <div
                  className="h-64 flex items-center justify-center text-sm"
                  style={{ color: "#94a3b8" }}
                >
                  No classification data available
                </div>

              )}

            </ChartCard>

          </div>

        </>

      )}


      {/* ========================================
          RECENT ANALYSES
      ======================================== */}

      <div
        className="
          rounded-2xl
          p-6
          border
          border-slate-800/80
          bg-gradient-to-br
          from-slate-900/95
          via-slate-900/90
          to-slate-950/95
          shadow-lg
        "
      >

        <div className="flex justify-between items-center mb-5">

          <div>

            <h4
              className="text-base font-bold tracking-tight"
              style={{ color: "#f1f5f9" }}
            >
              Recent Spatial Analyses
            </h4>

            <p
              className="text-xs font-semibold mt-1"
              style={{ color: "#94a3b8" }}
            >
              Classification reports generated from completed analyses
            </p>

          </div>

          <a
            href="#/reports"
            className="
              text-xs
              font-bold
              text-green-400
              hover:text-green-300
              transition-colors
              uppercase
              tracking-wider
            "
          >
            All Reports →
          </a>

        </div>


        <div className="overflow-x-auto -mx-6">

          <table className="w-full text-left border-collapse min-w-[700px]">

            <thead>

              <tr
                className="
                  border-b
                  border-slate-800
                  text-[10px]
                  font-bold
                  uppercase
                  tracking-widest
                  bg-slate-950/30
                "
                style={{ color: "#94a3b8" }}
              >

                <th className="py-3 px-6">
                  Report ID
                </th>

                <th className="py-3 px-6">
                  Village
                </th>

                <th className="py-3 px-6">
                  District / State
                </th>

                <th className="py-3 px-6">
                  Date Mapped
                </th>

                <th className="py-3 px-6 text-right">
                  Coverage (Ha)
                </th>

                <th className="py-3 px-6 text-right">
                  AI Confidence
                </th>

                <th className="py-3 px-6 text-center">
                  Status
                </th>

              </tr>

            </thead>


            <tbody>

              {recentAnalyses.length > 0 ? (

                recentAnalyses.map((report) => (

                  <tr
                    key={report.id}
                    className="
                      border-b
                      border-slate-800/70
                      last:border-0
                      hover:bg-slate-800/30
                      transition-colors
                      text-xs
                      font-semibold
                    "
                  >

                    {/* REPORT ID */}

                    <td
                      className="py-4 px-6 font-mono font-bold"
                      style={{ color: "#34d399" }}
                    >
                      #{report.id}
                    </td>


                    {/* VILLAGE */}

                    <td
                      className="py-4 px-6 font-bold"
                      style={{ color: "#f1f5f9" }}
                    >
                      {report.village}
                    </td>


                    {/* DISTRICT / STATE */}

                    <td
                      className="py-4 px-6 font-semibold"
                      style={{ color: "#cbd5e1" }}
                    >
                      {report.district}, {report.state}
                    </td>


                    {/* DATE */}

                    <td
                      className="py-4 px-6 font-medium"
                      style={{ color: "#94a3b8" }}
                    >
                      {report.date
                        ? String(report.date).split("T")[0]
                        : "—"}
                    </td>


                    {/* AREA */}

                    <td
                      className="py-4 px-6 text-right font-semibold"
                      style={{ color: "#cbd5e1" }}
                    >
                      {Number(
                        report.total_area || 0
                      ).toFixed(2)}{" "}
                      Ha
                    </td>


                    {/* CONFIDENCE */}

                    <td
                      className="py-4 px-6 text-right font-bold"
                      style={{ color: "#34d399" }}
                    >
                      {Number(
                        report.confidence || 0
                      ).toFixed(2)}%
                    </td>


                    {/* STATUS */}

                    <td className="py-4 px-6 text-center">

                      <span
                        className={`
                          inline-flex
                          items-center
                          gap-1.5
                          px-2.5
                          py-1
                          rounded-full
                          border
                          text-[9px]
                          font-bold
                          uppercase
                          tracking-wider
                          ${getStatusClass(
                          report.status
                        )}
                        `}
                      >

                        <span className="w-1.5 h-1.5 rounded-full bg-current" />

                        {getStatusLabel(
                          report.status
                        )}

                      </span>

                    </td>

                  </tr>

                ))

              ) : (

                <tr>

                  <td
                    colSpan="7"
                    className="text-center py-10 font-medium"
                    style={{ color: "#94a3b8" }}
                  >
                    {searchQuery
                      ? "No matching GIS records found."
                      : "No analyses have been performed yet."}
                  </td>

                </tr>

              )}

            </tbody>

          </table>

        </div>

      </div>


      {/* ========================================
          TOAST
      ======================================== */}

      {toastMessage && (

        <NotificationToast
          message={toastMessage}
          type={toastType}
          onClose={() =>
            setToastMessage("")
          }
        />

      )}

    </div>
  );
};


export default Dashboard;
