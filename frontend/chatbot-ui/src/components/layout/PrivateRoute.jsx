import React from "react";
import MainLayout from "./MainLayout";

/**
 * Artık kimlik doğrulama gerektirmeyen, sadece MainLayout'u saran bileşen
 */
const PrivateRoute = ({ children }) => {
  // Doğrudan MainLayout içinde içeriği render et
  return <MainLayout>{children}</MainLayout>;
};

export default PrivateRoute;
