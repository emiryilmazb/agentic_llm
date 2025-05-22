import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  AppBar,
  Box,
  CssBaseline,
  Drawer,
  IconButton,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
} from "@mui/material";

// Icons
import MenuIcon from "@mui/icons-material/Menu";
import ChatIcon from "@mui/icons-material/Chat";
import PersonIcon from "@mui/icons-material/Person";
import BuildIcon from "@mui/icons-material/Build";
import SettingsIcon from "@mui/icons-material/Settings";

// Hooks
import { useCharacter } from "../../contexts/CharacterContext";

const drawerWidth = 280;

/**
 * MainLayout component that provides a consistent layout for authenticated pages
 * Includes a responsive drawer, app bar, and main content area
 */
const MainLayout = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedCharacter } = useCharacter();
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigate = (path) => {
    navigate(path);
    setMobileOpen(false);
  };

  // Navigation items for the sidebar
  const navItems = [
    {
      text: "Chat",
      icon: <ChatIcon />,
      path: "/",
      active: location.pathname === "/",
    },
    {
      text: "Characters",
      icon: <PersonIcon />,
      path: "/characters",
      active: location.pathname.includes("/characters"),
    },
    {
      text: "Tools",
      icon: <BuildIcon />,
      path: "/tools",
      active: location.pathname.includes("/tools"),
    },
    {
      text: "Settings",
      icon: <SettingsIcon />,
      path: "/settings",
      active: location.pathname === "/settings",
    },
  ];

  // Drawer content - used for both permanent and temporary drawers
  const drawer = (
    <div>
      <Toolbar className="flex justify-center items-center py-4">
        <Typography
          variant="h5"
          component="div"
          className="font-bold text-primary"
        >
          AI Chatbot
        </Typography>
      </Toolbar>
      <Divider />
      
      {/* Selected Character Section */}
      <Box className="px-4 py-3 bg-gray-50">
        <Typography variant="subtitle2" className="text-gray-500 mb-2">
          Current Character
        </Typography>
        <div className="flex items-center">
          <Avatar
            src={selectedCharacter?.avatar || ""}
            className="mr-2"
            alt={selectedCharacter?.name || "No character selected"}
          >
            {!selectedCharacter && <PersonIcon />}
          </Avatar>
          <div>
            <Typography variant="subtitle1" className="font-medium">
              {selectedCharacter?.name || "No character selected"}
            </Typography>
            {selectedCharacter && (
              <Typography variant="body2" className="text-gray-500 text-xs">
                {selectedCharacter.personality}
              </Typography>
            )}
          </div>
        </div>
      </Box>
      
      <Divider />
      
      {/* Navigation Links */}
      <List>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              onClick={() => handleNavigate(item.path)}
              className={`${
                item.active ? "bg-primary-light bg-opacity-10" : ""
              }`}
            >
              <ListItemIcon
                className={`${item.active ? "text-primary" : "text-gray-500"}`}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                className={`${item.active ? "text-primary" : "text-gray-700"}`}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      
      {/* Kullanıcı bölümü kaldırıldı */}
    </div>
  );

  return (
    <Box className="flex">
      <CssBaseline />
      
      {/* App Bar - only visible on mobile */}
      <AppBar
        position="fixed"
        className="md:hidden bg-white text-gray-900 shadow-sm"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            className="mr-2 md:hidden"
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" className="flex-grow">
            AI Chatbot
          </Typography>
          {/* Kullanıcı menüsü kaldırıldı */}
        </Toolbar>
      </AppBar>
      
      {/* Mobile Drawer */}
      <Box
        component="nav"
        className="md:w-[280px] md:flex-shrink-0"
        aria-label="navigation drawer"
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: "block", md: "none" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
            },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer - permanently visible */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: "none", md: "block" },
            "& .MuiDrawer-paper": {
              boxSizing: "border-box",
              width: drawerWidth,
              borderRight: "1px solid rgba(0, 0, 0, 0.12)",
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      
      {/* Main content area */}
      <Box
        component="main"
        className="flex-grow bg-background min-h-screen"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
        }}
      >
        <Toolbar className="md:hidden" /> {/* Space for the app bar on mobile */}
        <Box className="p-4 h-full">{children}</Box>
      </Box>
    </Box>
  );
};

export default MainLayout;
