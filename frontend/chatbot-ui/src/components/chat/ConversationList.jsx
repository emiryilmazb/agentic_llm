import React, { useState } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  InputBase,
  Divider,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Clear as ClearIcon,
} from "@mui/icons-material";
import { useChat } from "../../contexts/ChatContext";
import { useCharacter } from "../../contexts/CharacterContext";
import { motion } from "framer-motion";

const ConversationList = () => {
  const {
    conversations,
    activeConversation,
    selectConversation,
    deleteConversation,
    renameConversation,
    createConversation,
    clearConversation,
    loading,
    error
  } = useChat();
  const { selectedCharacter } = useCharacter();
  const [searchTerm, setSearchTerm] = useState("");
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [isRenaming, setIsRenaming] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  
  console.log("ConversationList render - conversations:", conversations);
  console.log("ConversationList render - activeConversation:", activeConversation);
  console.log("ConversationList render - selectedCharacter:", selectedCharacter);

  // Filter conversations based on search term
  const filteredConversations = conversations.filter((conv) =>
    conv.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleMenuOpen = (event, conversationId) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
    setSelectedConversationId(conversationId);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedConversationId(null);
  };

  const handleDelete = async () => {
    if (selectedConversationId) {
      console.log("Konuşma siliniyor:", selectedConversationId);
      // API kılavuzuna göre konuşma silme
      await deleteConversation(selectedConversationId);
      handleMenuClose();
    }
  };

  const handleRenameClick = () => {
    const conversation = conversations.find(
      (conv) => conv.id === selectedConversationId
    );
    if (conversation) {
      setNewTitle(conversation.title);
      setIsRenaming(true);
      handleMenuClose();
    }
  };

  const handleRenameSubmit = async (e) => {
    e.preventDefault();
    if (selectedConversationId && newTitle.trim()) {
      console.log("Konuşma yeniden adlandırılıyor:", selectedConversationId, newTitle.trim());
      // API kılavuzuna göre konuşma başlığını güncelleme
      await renameConversation(selectedConversationId, newTitle.trim());
      setIsRenaming(false);
      setSelectedConversationId(null);
    }
  };

  const handleRenameCancel = () => {
    setIsRenaming(false);
    setSelectedConversationId(null);
  };

  return (
    <Box className="h-full flex flex-col">
      {/* Header */}
      <Box className="p-4 border-b border-gray-200">
        <Typography variant="h6" className="font-semibold">
          Konuşmalar
        </Typography>
      </Box>

      {/* Search Box */}
      <Box className="px-4 py-2 border-b border-gray-200">
        <Box className="flex items-center bg-gray-100 rounded-lg px-3 py-1">
          <SearchIcon className="text-gray-400 mr-2" fontSize="small" />
          <InputBase
            placeholder="Konuşmalarda ara..."
            className="flex-1 text-sm"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Box>
      </Box>

      {/* New Chat Button */}
      <Box className="px-4 py-2">
        <Button
          variant="contained"
          color="primary"
          fullWidth
          startIcon={<AddIcon />}
          onClick={() => {
            console.log("Yeni Konuşma butonu tıklandı");
            // API kılavuzuna göre yeni konuşma oluşturma
            createConversation("Yeni Konuşma");
          }}
          disabled={!selectedCharacter || loading}
          className="py-2"
        >
          Yeni Konuşma
        </Button>
        {!selectedCharacter && (
          <Typography variant="caption" className="text-error-light text-center block mt-1">
            Lütfen önce bir karakter seçin
          </Typography>
        )}
      </Box>

      <Divider className="my-2" />

      {/* Error Message */}
      {error && (
        <Alert severity="error" className="mx-4 my-2">
          {error}
        </Alert>
      )}

      {/* Conversation List */}
      <List className="flex-1 overflow-y-auto">
        {loading ? (
          <Box className="flex justify-center items-center h-32">
            <CircularProgress size={32} />
          </Box>
        ) : filteredConversations.length > 0 ? (
          filteredConversations.map((conversation) => (
            <motion.div
              key={conversation.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              {isRenaming && selectedConversationId === conversation.id ? (
                <ListItem className="py-2">
                  <form
                    onSubmit={handleRenameSubmit}
                    className="w-full flex items-center"
                  >
                    <InputBase
                      autoFocus
                      value={newTitle}
                      onChange={(e) => setNewTitle(e.target.value)}
                      className="flex-1 px-2 py-1 border rounded-md"
                    />
                    <Box className="flex ml-1">
                      <IconButton
                        size="small"
                        color="primary"
                        type="submit"
                        className="text-success"
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={handleRenameCancel}
                        className="text-error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </form>
                </ListItem>
              ) : (
                <ListItem disablePadding>
                  <ListItemButton
                    selected={activeConversation?.id === conversation.id}
                    className={`rounded-lg my-1 ${
                      activeConversation?.id === conversation.id
                        ? "bg-primary-light bg-opacity-10"
                        : ""
                    }`}
                    onClick={() => {
                      console.log("Konuşma seçildi:", conversation);
                      selectConversation(conversation);
                    }}
                  >
                    <ListItemAvatar>
                      <Avatar className="bg-primary text-white">
                        {conversation.character_name ? conversation.character_name.charAt(0).toUpperCase() : "C"}
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={conversation.title}
                      secondary={`${conversation.character_name} • ${new Date(
                        conversation.updated_at
                      ).toLocaleDateString()}`}
                      primaryTypographyProps={{
                        noWrap: true,
                        className: "font-medium",
                      }}
                      secondaryTypographyProps={{
                        noWrap: true,
                        className: "text-xs",
                      }}
                    />
                    <IconButton
                      edge="end"
                      aria-label="conversation menu"
                      onClick={(e) => handleMenuOpen(e, conversation.id)}
                      className="ml-1"
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </ListItemButton>
                </ListItem>
              )}
            </motion.div>
          ))
        ) : (
          <Box className="text-center p-4">
            <Typography variant="body2" className="text-gray-500">
              {searchTerm
                ? "Aramanızla eşleşen konuşma bulunamadı"
                : "Henüz konuşma bulunmuyor"}
            </Typography>
          </Box>
        )}
      </List>

      {/* Conversation Menu */}
      <Menu
        anchorEl={menuAnchorEl}
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
        <MenuItem onClick={handleRenameClick} className="text-sm">
          <EditIcon fontSize="small" className="mr-2 text-primary" />
          Yeniden Adlandır
        </MenuItem>
        <MenuItem
          onClick={() => {
            if (selectedConversationId) {
              console.log("Konuşma temizleniyor:", selectedConversationId);
              // API kılavuzuna göre konuşma geçmişini temizleme
              clearConversation(selectedConversationId);
              handleMenuClose();
            }
          }}
          className="text-sm"
        >
          <ClearIcon fontSize="small" className="mr-2 text-warning" />
          Konuşmayı Temizle
        </MenuItem>
        <MenuItem onClick={handleDelete} className="text-sm">
          <DeleteIcon fontSize="small" className="mr-2 text-error" />
          Sil
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default ConversationList;
