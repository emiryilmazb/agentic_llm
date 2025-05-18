import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";

// Context Providers
import { AuthProvider } from "./contexts/AuthContext";
import { ChatProvider } from "./contexts/ChatContext";
import { CharacterProvider } from "./contexts/CharacterContext";
import { ToolProvider } from "./contexts/ToolContext";

// Pages
import ChatPage from "./pages/ChatPage";
import CharactersPage from "./pages/CharactersPage";
import CreateCharacterPage from "./pages/CreateCharacterPage";
import ToolsPage from "./pages/ToolsPage";
import CreateToolPage from "./pages/CreateToolPage";
import SettingsPage from "./pages/SettingsPage";
import NotFoundPage from "./pages/NotFoundPage";

// Components
import PrivateRoute from "./components/layout/PrivateRoute";

// Create theme
const theme = createTheme({
  palette: {
    primary: {
      light: "#6366f1",
      main: "#4f46e5",
      dark: "#4338ca",
      contrastText: "#fff",
    },
    secondary: {
      light: "#f3f4f6",
      main: "#e5e7eb",
      dark: "#d1d5db",
      contrastText: "#111827",
    },
    background: {
      default: "#f9fafb",
      paper: "#ffffff",
    },
  },
  typography: {
    fontFamily: "'Inter', sans-serif",
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 500,
    },
    h5: {
      fontWeight: 500,
    },
    h6: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: "none",
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: "0 0 15px rgba(0, 0, 0, 0.05)",
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <AuthProvider>
        <CharacterProvider>
          <ToolProvider>
            <ChatProvider>
              <Routes>
                {/* Tüm rotalar artık PrivateRoute ile korunuyor, ancak kimlik doğrulama kontrolü yok */}
                <Route
                  path="/"
                  element={
                    <PrivateRoute>
                      <ChatPage />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/characters"
                  element={
                    <PrivateRoute>
                      <CharactersPage />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/characters/create"
                  element={
                    <PrivateRoute>
                      <CreateCharacterPage />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/tools"
                  element={
                    <PrivateRoute>
                      <ToolsPage />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/tools/create"
                  element={
                    <PrivateRoute>
                      <CreateToolPage />
                    </PrivateRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <PrivateRoute>
                      <SettingsPage />
                    </PrivateRoute>
                  }
                />

                {/* 404 Page */}
                <Route path="/404" element={<NotFoundPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </ChatProvider>
          </ToolProvider>
        </CharacterProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
