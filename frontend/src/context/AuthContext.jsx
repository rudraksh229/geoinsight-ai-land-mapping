import React, {
  createContext,
  useContext,
  useState,
  useEffect,
} from "react";

import { getCurrentUser } from "../services/authService";

const AuthContext = createContext(null);


export const useAuth = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used within an AuthProvider"
    );
  }

  return context;
};


export const AuthProvider = ({ children }) => {

  const [user, setUser] = useState(null);

  const [isAuthenticated, setIsAuthenticated] =
    useState(false);

  const [loading, setLoading] =
    useState(true);


  // ==========================================
  // RESTORE SESSION
  // ==========================================

  useEffect(() => {

    const restoreSession = async () => {

      const token =
        localStorage.getItem("token");

      if (!token) {

        setUser(null);
        setIsAuthenticated(false);
        setLoading(false);

        return;
      }


      try {

        const response =
          await getCurrentUser();

        setUser(response.data);

        setIsAuthenticated(true);

      } catch (error) {

        console.error(
          "Session validation failed:",
          error
        );

        // Remove invalid / expired token
        localStorage.removeItem("token");

        setUser(null);
        setIsAuthenticated(false);

      } finally {

        setLoading(false);

      }

    };


    restoreSession();

  }, []);


  // ==========================================
  // LOGIN
  // ==========================================

  const loginAuth = async (
    token,
    userData = null
  ) => {

    if (!token) {
      return;
    }

    localStorage.setItem(
      "token",
      token
    );


    try {

      if (userData) {

        setUser(userData);

      } else {

        const response =
          await getCurrentUser();

        setUser(response.data);

      }

      setIsAuthenticated(true);

    } catch (error) {

      console.error(
        "User verification failed:",
        error
      );

      localStorage.removeItem("token");

      setUser(null);
      setIsAuthenticated(false);

      throw error;
    }

  };


  // ==========================================
  // LOGOUT
  // ==========================================

  const logout = () => {

    localStorage.removeItem("token");

    setUser(null);

    setIsAuthenticated(false);

  };


  // ==========================================
  // CHANGE PASSWORD
  // ==========================================

  const changePassword = async () => {

    throw new Error(
      "Change password API is not implemented yet."
    );

  };


  // ==========================================
  // UPDATE PROFILE
  // ==========================================

  const updateProfile = (
    updatedDetails
  ) => {

    setUser((prev) => ({
      ...prev,
      ...updatedDetails,
    }));

  };


  const value = {

    user,

    isAuthenticated,

    loading,

    loginAuth,

    logout,

    changePassword,

    updateProfile,

  };


  return (

    <AuthContext.Provider value={value}>

      {!loading && children}

    </AuthContext.Provider>

  );

};