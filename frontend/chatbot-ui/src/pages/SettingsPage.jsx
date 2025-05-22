import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  Divider,
  FormControl,
  Select,
  MenuItem,
  Button,
  TextField,
  Snackbar,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import {
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon,
  FormatSize as FormatSizeIcon,
  Notifications as NotificationsIcon,
  Logout as LogoutIcon,
  Delete as DeleteIcon,
  Security as SecurityIcon,
  AccountCircle as AccountCircleIcon,
} from "@mui/icons-material";
import { useAuth } from "../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

const SettingsPage = () => {
  const { currentUser, updateUserPreferences, logout } = useAuth();
  const navigate = useNavigate();

  const [userPreferences, setUserPreferences] = useState({
    theme: "light",
    fontSize: "medium",
    notifications: true,
  });
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [passwordValues, setPasswordValues] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [passwordErrors, setPasswordErrors] = useState({});
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  // Load user preferences
  useEffect(() => {
    if (currentUser?.preferences) {
      setUserPreferences(currentUser.preferences);
    }
  }, [currentUser]);

  const handlePreferenceChange = async (name, value) => {
    const updatedPreferences = {
      ...userPreferences,
      [name]: value,
    };
    
    setUserPreferences(updatedPreferences);
    
    // Save preferences to backend
    const success = await updateUserPreferences(updatedPreferences);
    if (success) {
      setSuccessMessage("Preferences updated successfully");
      setShowSuccess(true);
    }
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordValues({
      ...passwordValues,
      [name]: value,
    });
    
    // Clear errors when field is edited
    if (passwordErrors[name]) {
      setPasswordErrors({
        ...passwordErrors,
        [name]: null,
      });
    }
  };

  const validatePasswordForm = () => {
    const errors = {};
    
    if (!passwordValues.currentPassword) {
      errors.currentPassword = "Current password is required";
    }
    
    if (!passwordValues.newPassword) {
      errors.newPassword = "New password is required";
    } else if (passwordValues.newPassword.length < 6) {
      errors.newPassword = "Password must be at least 6 characters";
    }
    
    if (!passwordValues.confirmPassword) {
      errors.confirmPassword = "Please confirm your new password";
    } else if (passwordValues.newPassword !== passwordValues.confirmPassword) {
      errors.confirmPassword = "Passwords do not match";
    }
    
    setPasswordErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }
    
    // In a real app, call API to update password
    // const success = await updatePassword(passwordValues.currentPassword, passwordValues.newPassword);
    
    // Mock successful update
    setSuccessMessage("Password updated successfully");
    setShowSuccess(true);
    setPasswordValues({
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    });
  };

  const handleAccountDelete = () => {
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = () => {
    // In a real app, call API to delete account
    // const success = await deleteAccount();
    
    setShowDeleteConfirm(false);
    logout();
    navigate("/login");
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <Box className="p-6">
      <Typography variant="h4" component="h1" className="font-bold mb-6">
        Settings
      </Typography>

      {/* App Preferences */}
      <Paper className="p-6 mb-6 rounded-xl">
        <Typography variant="h6" className="font-semibold mb-4">
          App Preferences
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              {userPreferences.theme === "dark" ? (
                <DarkModeIcon />
              ) : (
                <LightModeIcon />
              )}
            </ListItemIcon>
            <ListItemText
              primary="Dark Mode"
              secondary="Toggle between light and dark theme"
            />
            <Switch
              edge="end"
              checked={userPreferences.theme === "dark"}
              onChange={(e) =>
                handlePreferenceChange("theme", e.target.checked ? "dark" : "light")
              }
            />
          </ListItem>
          <Divider variant="inset" component="li" />
          <ListItem>
            <ListItemIcon>
              <FormatSizeIcon />
            </ListItemIcon>
            <ListItemText primary="Font Size" secondary="Adjust text size" />
            <Box sx={{ minWidth: 120 }}>
              <FormControl fullWidth size="small">
                <Select
                  value={userPreferences.fontSize}
                  onChange={(e) => handlePreferenceChange("fontSize", e.target.value)}
                >
                  <MenuItem value="small">Small</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="large">Large</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </ListItem>
          <Divider variant="inset" component="li" />
          <ListItem>
            <ListItemIcon>
              <NotificationsIcon />
            </ListItemIcon>
            <ListItemText
              primary="Notifications"
              secondary="Enable or disable notifications"
            />
            <Switch
              edge="end"
              checked={userPreferences.notifications}
              onChange={(e) =>
                handlePreferenceChange("notifications", e.target.checked)
              }
            />
          </ListItem>
        </List>
      </Paper>

      {/* Account Settings */}
      <Paper className="p-6 mb-6 rounded-xl">
        <Typography variant="h6" className="font-semibold mb-4">
          Account Settings
        </Typography>
        
        {/* User Info */}
        <Box className="flex items-center mb-6">
          <AccountCircleIcon fontSize="large" className="text-primary mr-4" />
          <Box>
            <Typography variant="h6">{currentUser?.username || "User"}</Typography>
            <Typography variant="body2" color="textSecondary">
              {currentUser?.email || "email@example.com"}
            </Typography>
          </Box>
        </Box>
        
        <Divider className="mb-6" />
        
        {/* Change Password */}
        <Typography variant="subtitle1" className="font-medium mb-3">
          Change Password
        </Typography>
        <form onSubmit={handlePasswordSubmit}>
          <TextField
            label="Current Password"
            type="password"
            name="currentPassword"
            value={passwordValues.currentPassword}
            onChange={handlePasswordChange}
            fullWidth
            margin="normal"
            error={!!passwordErrors.currentPassword}
            helperText={passwordErrors.currentPassword}
          />
          <TextField
            label="New Password"
            type="password"
            name="newPassword"
            value={passwordValues.newPassword}
            onChange={handlePasswordChange}
            fullWidth
            margin="normal"
            error={!!passwordErrors.newPassword}
            helperText={passwordErrors.newPassword}
          />
          <TextField
            label="Confirm New Password"
            type="password"
            name="confirmPassword"
            value={passwordValues.confirmPassword}
            onChange={handlePasswordChange}
            fullWidth
            margin="normal"
            error={!!passwordErrors.confirmPassword}
            helperText={passwordErrors.confirmPassword}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            className="mt-3"
            startIcon={<SecurityIcon />}
          >
            Update Password
          </Button>
        </form>
      </Paper>

      {/* Account Actions */}
      <Paper className="p-6 rounded-xl">
        <Typography variant="h6" className="font-semibold mb-4">
          Account Actions
        </Typography>
        <Box className="flex flex-col sm:flex-row gap-4">
          <Button
            variant="outlined"
            color="primary"
            startIcon={<LogoutIcon />}
            onClick={handleLogout}
            className="flex-1"
          >
            Logout
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleAccountDelete}
            className="flex-1"
          >
            Delete Account
          </Button>
        </Box>
      </Paper>

      {/* Delete Account Confirmation Dialog */}
      <Dialog
        open={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
      >
        <DialogTitle>Delete Your Account?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            This action cannot be undone. All your data, including conversations,
            characters, and tools will be permanently deleted.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setShowDeleteConfirm(false)}
            color="primary"
          >
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            autoFocus
          >
            Delete Account
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={3000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity="success">{successMessage}</Alert>
      </Snackbar>
    </Box>
  );
};

export default SettingsPage;
