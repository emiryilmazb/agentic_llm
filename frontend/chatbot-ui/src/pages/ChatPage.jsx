import React, { useState, useEffect } from "react";
import { Box, Paper, Typography, Snackbar, Alert } from "@mui/material";
import { useChat } from "../contexts/ChatContext";
import { useCharacter } from "../contexts/CharacterContext";

// Components
import ConversationList from "../components/chat/ConversationList";
import ChatHeader from "../components/chat/ChatHeader";
import MessageList from "../components/chat/MessageList";
import ChatInput from "../components/chat/ChatInput";
import WelcomeScreen from "../components/chat/WelcomeScreen";

const ChatPage = () => {
  const { activeConversation, error, createConversation } = useChat();
  const { selectedCharacter, characters } = useCharacter();
  const [showError, setShowError] = useState(false);

  // Show error snackbar when error state changes
  useEffect(() => {
    if (error) {
      setShowError(true);
    }
  }, [error]);

  const handleCloseError = () => {
    setShowError(false);
  };

  const handleStartNewChat = async () => {
    if (!selectedCharacter) {
      return;
    }
    await createConversation(selectedCharacter);
  };

  return (
    <Box className="h-[calc(100vh-64px)] flex flex-col md:flex-row">
      {/* Conversation List - Hidden on mobile */}
      <Box
        className="hidden md:block w-80 h-full overflow-y-auto border-r border-gray-200"
        sx={{ display: { xs: "none", md: "block" } }}
      >
        <ConversationList onNewChat={handleStartNewChat} />
      </Box>

      {/* Chat Area */}
      <Box className="flex-1 flex flex-col h-full overflow-hidden">
        {activeConversation ? (
          <>
            {/* Chat Header */}
            <ChatHeader
              title={activeConversation.title}
              character={selectedCharacter}
              onNewChat={handleStartNewChat}
            />

            {/* Messages Container */}
            <Box className="flex-1 overflow-y-auto p-4 bg-gray-50">
              <MessageList />
            </Box>

            {/* Chat Input */}
            <Box className="p-4 border-t border-gray-200 bg-white">
              <ChatInput />
            </Box>
          </>
        ) : (
          // Welcome screen when no conversation is active
          <WelcomeScreen
            onStartNewChat={handleStartNewChat}
            hasCharacters={characters.length > 0}
          />
        )}
      </Box>

      {/* Error Snackbar */}
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={handleCloseError}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert onClose={handleCloseError} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ChatPage;
