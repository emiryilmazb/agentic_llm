import React, { useState } from "react";
import {
  Box,
  Typography,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
} from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  Person as PersonIcon,
  Menu as MenuIcon,
} from "@mui/icons-material";
import { useChat } from "../../contexts/ChatContext";

const ChatHeader = ({ title, character, onNewChat }) => {
  const { clearConversation, deleteConversation, activeConversation } = useChat();
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleMenuOpen = (event) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleClearChat = () => {
    clearConversation();
    handleMenuClose();
  };

  const handleDeleteChat = async () => {
    if (activeConversation) {
      await deleteConversation(activeConversation.id);
      handleMenuClose();
    }
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <Box className="p-3 border-b border-gray-200 bg-white flex items-center justify-between">
      <Box className="flex items-center">
        {/* Mobile menu button - only visible on mobile */}
        <IconButton
          className="mr-2 md:hidden"
          onClick={toggleMobileMenu}
          aria-label="open drawer"
        >
          <MenuIcon />
        </IconButton>

        {/* Character Avatar */}
        <Avatar
          src={character?.avatar || ""}
          className="mr-3"
          alt={character?.name || "Character"}
        >
          {!character?.avatar && <PersonIcon />}
        </Avatar>

        {/* Conversation Info */}
        <Box>
          <Typography variant="subtitle1" className="font-medium">
            {title || "New Conversation"}
          </Typography>
          {character && (
            <Typography variant="caption" className="text-gray-500 block">
              Chatting with {character.name}
            </Typography>
          )}
        </Box>
      </Box>

      {/* Action Buttons */}
      <Box className="flex items-center">
        <Tooltip title="New Chat">
          <IconButton onClick={onNewChat} className="text-primary">
            <AddIcon />
          </IconButton>
        </Tooltip>

        <Tooltip title="Chat Options">
          <IconButton
            onClick={handleMenuOpen}
            aria-label="chat options"
            aria-controls="chat-menu"
            aria-haspopup="true"
          >
            <MoreVertIcon />
          </IconButton>
        </Tooltip>

        {/* Chat Options Menu */}
        <Menu
          id="chat-menu"
          anchorEl={menuAnchorEl}
          keepMounted
          open={Boolean(menuAnchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: "bottom",
            horizontal: "right",
          }}
          transformOrigin={{
            vertical: "top",
            horizontal: "right",
          }}
        >
          <MenuItem onClick={handleClearChat} className="text-sm">
            Clear chat
          </MenuItem>
          <MenuItem onClick={handleDeleteChat} className="text-sm text-error">
            <DeleteIcon fontSize="small" className="mr-2" />
            Delete chat
          </MenuItem>
        </Menu>
      </Box>
    </Box>
  );
};

export default ChatHeader;
