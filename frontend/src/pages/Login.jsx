import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login as loginService } from "../services/authService";
import { useAuth } from "../context/AuthContext";
import ModalDialog from "../components/ModalDialog";
import NotificationToast from "../components/NotificationToast";

const Login = () => {
  const navigate = useNavigate();
  const { loginAuth } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [isForgotModalOpen, setIsForgotModalOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState("");
  const [resetSent, setResetSent] = useState(false);

  const [toastMessage, setToastMessage] = useState("");
  const [toastType, setToastType] = useState("success");

  const showToast = (message, type = "success") => {
    setToastMessage(message);
    setToastType(type);
  };

  // ============================
  // LOGIN
  // ============================
  const handleLoginSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      showToast("Please enter email and password.", "error");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await loginService({
        email,
        password,
      });

      console.log("Login response:", response.data);

      const token = response.data.access_token;

      if (!token) {
        throw new Error("Access token was not received.");
      }

      loginAuth(token, response.data.user || null);

      showToast("Login successful! Redirecting...", "success");

      setTimeout(() => {
        navigate("/", { replace: true });
      }, 800);
    } catch (error) {
      console.error("Login error:", error);

      const message =
        error.response?.data?.detail ||
        "Invalid email or password.";

      showToast(message, "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  // ============================
  // CREATE ACCOUNT
  // ============================
  const handleCreateAccount = () => {
    navigate("/register");
  };

  // ============================
  // FORGOT PASSWORD
  // ============================
  const handleForgotPasswordSubmit = (e) => {
    e.preventDefault();

    if (!resetEmail) {
      showToast("Please enter a valid email address.", "error");
      return;
    }

    setResetSent(true);

    showToast(
      `Password reset link dispatched to ${resetEmail}`,
      "success"
    );

    setTimeout(() => {
      setIsForgotModalOpen(false);
      setResetSent(false);
      setResetEmail("");
    }, 2000);
  };

  return (
    <>
      {/* =====================================================
          LOGIN PAGE ANIMATIONS
      ====================================================== */}
      <style>{`
        @keyframes gisScan {
          0% {
            transform: translateY(-120%);
            opacity: 0;
          }
          15% {
            opacity: 0.7;
          }
          50% {
            opacity: 1;
          }
          85% {
            opacity: 0.7;
          }
          100% {
            transform: translateY(120%);
            opacity: 0;
          }
        }

        @keyframes radarPulse {
          0% {
            transform: scale(0.8);
            opacity: 0.7;
          }
          70% {
            transform: scale(1.35);
            opacity: 0;
          }
          100% {
            transform: scale(1.35);
            opacity: 0;
          }
        }

        @keyframes radarPulse2 {
          0% {
            transform: scale(0.8);
            opacity: 0.5;
          }
          70% {
            transform: scale(1.7);
            opacity: 0;
          }
          100% {
            transform: scale(1.7);
            opacity: 0;
          }
        }

        @keyframes floatPoint {
          0%, 100% {
            transform: translate3d(0, 0, 0);
            opacity: 0.25;
          }
          50% {
            transform: translate3d(0, -18px, 0);
            opacity: 0.8;
          }
        }

        @keyframes floatPointReverse {
          0%, 100% {
            transform: translate3d(0, 0, 0);
            opacity: 0.2;
          }
          50% {
            transform: translate3d(0, 15px, 0);
            opacity: 0.7;
          }
        }

        @keyframes cardGlow {
          0%, 100% {
            box-shadow:
              0 0 0 1px rgba(34, 197, 94, 0.08),
              0 20px 60px rgba(0, 0, 0, 0.35);
          }
          50% {
            box-shadow:
              0 0 0 1px rgba(34, 197, 94, 0.25),
              0 0 35px rgba(34, 197, 94, 0.10),
              0 20px 60px rgba(0, 0, 0, 0.40);
          }
        }

        @keyframes dataBlink {
          0%, 100% {
            opacity: 0.25;
          }
          50% {
            opacity: 1;
          }
        }

        @keyframes targetRotate {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        .gis-scan-line {
          animation: gisScan 5s ease-in-out infinite;
        }

        .radar-pulse {
          animation: radarPulse 3s ease-out infinite;
        }

        .radar-pulse-2 {
          animation: radarPulse2 3s ease-out 1s infinite;
        }

        .gis-point {
          animation: floatPoint 4s ease-in-out infinite;
        }

        .gis-point-reverse {
          animation: floatPointReverse 5s ease-in-out infinite;
        }

        .login-card-glow {
          animation: cardGlow 4s ease-in-out infinite;
        }

        .data-blink {
          animation: dataBlink 2s ease-in-out infinite;
        }

        .target-rotate {
          animation: targetRotate 14s linear infinite;
        }

        @media (prefers-reduced-motion: reduce) {
          .gis-scan-line,
          .radar-pulse,
          .radar-pulse-2,
          .gis-point,
          .gis-point-reverse,
          .login-card-glow,
          .data-blink,
          .target-rotate {
            animation: none !important;
          }
        }
      `}</style>

      {/* =====================================================
          ANIMATED GIS BACKGROUND
      ====================================================== */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">

        {/* Soft green glow */}
        <div className="absolute -top-32 -left-32 w-80 h-80 rounded-full bg-green-500/10 blur-3xl" />

        {/* Soft cyan glow */}
        <div className="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-cyan-500/10 blur-3xl" />

        {/* GIS Grid */}
        <div
          className="absolute inset-0 opacity-[0.07]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(74, 222, 128, 0.35) 1px, transparent 1px),
              linear-gradient(90deg, rgba(74, 222, 128, 0.35) 1px, transparent 1px)
            `,
            backgroundSize: "55px 55px",
          }}
        />

        {/* Horizontal scanning beam */}
        <div
          className="gis-scan-line absolute left-0 right-0 h-32"
          style={{
            background:
              "linear-gradient(to bottom, transparent, rgba(34,197,94,0.08), rgba(34,197,94,0.16), rgba(34,197,94,0.05), transparent)",
          }}
        />

        {/* Floating GIS points */}
        <div className="gis-point absolute top-[18%] left-[12%] w-1.5 h-1.5 rounded-full bg-green-400 shadow-[0_0_12px_rgba(74,222,128,0.9)]" />
        <div className="gis-point-reverse absolute top-[30%] right-[15%] w-1 h-1 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.9)]" />
        <div
          className="gis-point absolute bottom-[25%] left-[18%] w-1 h-1 rounded-full bg-green-400"
          style={{ animationDelay: "1s" }}
        />
        <div
          className="gis-point-reverse absolute bottom-[18%] right-[22%] w-1.5 h-1.5 rounded-full bg-cyan-400"
          style={{ animationDelay: "1.5s" }}
        />
        <div
          className="data-blink absolute top-[45%] left-[8%] w-1 h-1 rounded-full bg-green-300"
        />
        <div
          className="data-blink absolute top-[62%] right-[10%] w-1 h-1 rounded-full bg-cyan-300"
          style={{ animationDelay: "0.8s" }}
        />

        {/* Radar rings behind card */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 sm:w-[500px] sm:h-[500px] rounded-full border border-green-400/10" />
        <div className="radar-pulse absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 sm:w-96 sm:h-96 rounded-full border border-green-400/20" />
        <div className="radar-pulse-2 absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 sm:w-96 sm:h-96 rounded-full border border-cyan-400/10" />
      </div>

      {/* =====================================================
          LOGIN CARD
      ====================================================== */}
      <div
        className="
          relative
          rounded-3xl
          p-8
          sm:p-10
          overflow-hidden
          bg-slate-950/90
          backdrop-blur-xl
          border border-slate-700/70
          login-card-glow
        "
      >

        {/* Top scanning line on card */}
        <div className="absolute top-0 left-0 right-0 h-px overflow-hidden">
          <div className="gis-scan-line h-full w-1/3 bg-gradient-to-r from-transparent via-green-400 to-transparent" />
        </div>

        {/* Card corner markers */}
        <div className="absolute top-4 left-4 w-5 h-5 border-l border-t border-green-500/40 rounded-tl-md" />
        <div className="absolute top-4 right-4 w-5 h-5 border-r border-t border-cyan-500/40 rounded-tr-md" />
        <div className="absolute bottom-4 left-4 w-5 h-5 border-l border-b border-cyan-500/40 rounded-bl-md" />
        <div className="absolute bottom-4 right-4 w-5 h-5 border-r border-b border-green-500/40 rounded-br-md" />

        {/* =================================================
            HEADER
        ================================================== */}
        <div className="text-center mb-8 relative">

          {/* GIS Target */}
          <div className="relative w-16 h-16 mx-auto mb-5 flex items-center justify-center">

            <div className="absolute inset-0 rounded-full border border-green-500/20" />

            <div className="absolute inset-2 rounded-full border border-cyan-400/20" />

            <div className="target-rotate absolute inset-1 border border-dashed border-green-400/40 rounded-full" />

            <div className="absolute w-8 h-8 rounded-full border border-green-400/40" />

            <div className="absolute w-1.5 h-1.5 rounded-full bg-green-400 shadow-[0_0_14px_rgba(74,222,128,1)]" />

            <div className="absolute w-12 h-px bg-green-400/30" />
            <div className="absolute h-12 w-px bg-green-400/30" />

          </div>

          <h2
            className="text-4xl font-black text-white tracking-tight leading-tight"
            style={{
              color: "#FFFFFF",
              textShadow: "0 0 8px rgba(255,255,255,0.35), 0 0 20px rgba(255,255,255,0.15)",
            }}
          >
            GeoInsight AI
          </h2>

          <p className="text-xs font-semibold text-slate-400 mt-2 uppercase tracking-wider">
            Sign in to Land Mapping Dashboard
          </p>

          {/* System status */}
          <div className="flex items-center justify-center gap-2 mt-4">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            <span className="text-[9px] text-green-400/80 uppercase tracking-[0.2em] font-bold">
              Satellite Intelligence Online
            </span>
          </div>
        </div>

        {/* =================================================
            LOGIN FORM
        ================================================== */}
        <form onSubmit={handleLoginSubmit} className="space-y-5">

          {/* EMAIL */}
          <div>
            <label
              htmlFor="email"
              className="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-2"
            >
              Government Email ID
            </label>

            <div className="relative">

              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
                  />
                </svg>
              </span>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-600 focus:border-green-500 focus:bg-slate-800 rounded-xl text-xs font-bold outline-none transition-all text-white caret-green-400 placeholder-slate-500 tech-mono"
                placeholder="officer.name@gov.in"
                autoComplete="email"
                required
              />
            </div>
          </div>

          {/* PASSWORD */}
          <div>
            <div className="flex justify-between items-center mb-2">

              <label
                htmlFor="password"
                className="block text-xs font-bold text-slate-300 uppercase tracking-wider"
              >
                Access PIN / Password
              </label>

              <button
                type="button"
                onClick={() => setIsForgotModalOpen(true)}
                className="
                  text-xs
                  font-bold
                  text-green-400
                  hover:text-green-300
                  transition-colors
                  cursor-pointer
                "
              >
                Forgot Password?
              </button>

            </div>

            <div className="relative">

              <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-500">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  className="w-5 h-5"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z"
                  />
                </svg>
              </span>

              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-600 focus:border-green-500 focus:bg-slate-800 rounded-xl text-xs font-bold outline-none transition-all text-white caret-green-400 placeholder-slate-500 tech-mono"
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>
          </div>

          {/* REMEMBER ME */}
          <div className="flex items-center justify-between py-1">

            <label className="flex items-center gap-2 cursor-pointer select-none text-slate-400">

              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="
                  rounded-sm
                  border-slate-600
                  text-green-500
                  focus:ring-green-500
                  w-4
                  h-4
                  bg-slate-900
                  cursor-pointer
                "
              />

              <span className="text-xs font-bold">
                Remember session
              </span>

            </label>


          </div>

          {/* LOGIN BUTTON */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="
              group
              relative
              w-full
              overflow-hidden
              bg-green-500/15
              hover:bg-green-500/25
              border border-green-500/50
              hover:border-green-400
              active:bg-green-500/30
              disabled:bg-slate-800
              disabled:border-slate-700
              text-green-400
              disabled:text-slate-500
              py-3
              px-4
              rounded-xl
              font-bold
              uppercase
              tracking-wider
              text-xs
              transition-all
              flex
              items-center
              justify-center
              gap-2
              cursor-pointer
              disabled:cursor-not-allowed
              shadow-[0_0_20px_rgba(34,197,94,0.08)]
              hover:shadow-[0_0_25px_rgba(34,197,94,0.16)]
            "
          >

            {/* Button scan effect */}
            <span className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 bg-gradient-to-r from-transparent via-green-400/10 to-transparent" />

            {isSubmitting ? (
              <>
                <svg
                  className="animate-spin h-5 w-5 text-green-400"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />

                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>

                <span>Verifying credentials...</span>
              </>
            ) : (
              <>
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
                    d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3.75-3l3 3m0 0l-3 3m3-3H12"
                  />
                </svg>

                <span>Authenticate & Login</span>
              </>
            )}

          </button>

          {/* CREATE ACCOUNT */}
          <div className="text-center pt-2">

            <p className="text-xs text-slate-500 font-semibold">

              Don't have an account?{" "}

              <button
                type="button"
                onClick={handleCreateAccount}
                className="
                  text-green-400
                  hover:text-green-300
                  font-bold
                  transition-colors
                  cursor-pointer
                "
              >
                Create Account
              </button>

            </p>

          </div>

        </form>
      </div>.

      

      {/* =====================================================
          FORGOT PASSWORD MODAL
      ====================================================== */}
      <ModalDialog
        isOpen={isForgotModalOpen}
        onClose={() => setIsForgotModalOpen(false)}
        title="Recover GIS Portal Credentials"
        footerButtons={
          <>
            <button
              onClick={() => setIsForgotModalOpen(false)}
              className="
                px-4
                py-2.5
                text-xs
                font-bold
                text-slate-500
                dark:text-slate-400
                hover:text-slate-700
                dark:hover:text-slate-200
                hover:bg-slate-200
                dark:hover:bg-slate-800
                bg-slate-100
                dark:bg-slate-800/40
                rounded-xl
                uppercase
                tracking-wider
                transition-colors
                cursor-pointer
              "
            >
              Cancel
            </button>

            <button
              onClick={handleForgotPasswordSubmit}
              className="
                px-4
                py-2.5
                text-xs
                font-bold
                text-white
                bg-green-600
                hover:bg-green-700
                rounded-xl
                uppercase
                tracking-wider
                shadow-sm
                transition-colors
                cursor-pointer
              "
            >
              Send Reset Link
            </button>
          </>
        }
      >

        {resetSent ? (

          <div className="text-center py-4">

            <div className="
              w-12
              h-12
              bg-green-100
              dark:bg-green-950/30
              text-green-700
              dark:text-green-400
              rounded-full
              flex
              items-center
              justify-center
              mx-auto
              mb-3
            ">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2.5}
                stroke="currentColor"
                className="w-6 h-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4.5 12.75l6 6 9-13.5"
                />
              </svg>
            </div>

            <p className="font-bold text-slate-800 dark:text-slate-100">
              Verification Link Dispatched!
            </p>

            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1.5 font-bold">
              Please check your official inbox for recovery instructions.
            </p>

          </div>

        ) : (

          <div className="space-y-4">

            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold leading-relaxed">
              Enter your registered government email address. We will
              transmit a recovery link to reset your Access PIN.
            </p>

            <div>

              <label
                htmlFor="reset-email"
                className="
                  block
                  text-[9px]
                  font-bold
                  text-slate-500
                  dark:text-slate-400
                  uppercase
                  tracking-widest
                  mb-1.5
                "
              >
                Official Email Address
              </label>

              <input
                id="reset-email"
                type="email"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                className="
                  w-full
                  px-3
                  py-2.5
                  bg-slate-50
                  dark:bg-slate-950
                  border
                  border-slate-200
                  dark:border-slate-800
                  focus:border-green-600
                  dark:focus:border-green-500
                  focus:ring-1
                  focus:ring-green-500/20
                  rounded-xl
                  text-xs
                  font-bold
                  outline-none
                  text-slate-800
                  dark:text-slate-100
                  placeholder-slate-400
                  dark:placeholder-slate-600
                "
                placeholder="name@gov.in"
                required
              />

            </div>

          </div>

        )}

      </ModalDialog>

      {/* =====================================================
          NOTIFICATION TOAST
      ====================================================== */}
      {toastMessage && (
        <NotificationToast
          message={toastMessage}
          type={toastType}
          onClose={() => setToastMessage("")}
        />
      )}

    </>
  );
};

export default Login;
