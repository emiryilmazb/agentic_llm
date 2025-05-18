import React, { createContext, useContext } from "react";
import axios from "axios";

const AuthContext = createContext(null);

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  // API base URL ayarı
  axios.defaults.baseURL = "http://localhost:8000";

  // Kullanıcı kimlik doğrulama olmadan doğrudan erişim sağlanacak
  const value = {
    // Boş değerler, kimlik doğrulama kaldırıldığı için
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
