import { createContext, useContext, useState } from "react";
import { login as apiLogin, getToken, removeToken } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(() => !!getToken());

  async function login(email, password) {
    await apiLogin(email, password);
    setIsLoggedIn(true);
  }

  function logout() {
    removeToken();
    setIsLoggedIn(false);
  }

  const value = { isLoggedIn, login, logout };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}