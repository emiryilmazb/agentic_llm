// This is an example implementation showing how to update ChatContext.js
// to work with the new conversation-based backend API

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import { useAuth } from "./AuthContext";
import { useCharacter } from "./CharacterContext";
import { useTool } from "./ToolContext";

const ChatContext = createContext(null);

export const useChat = () => {
  return useContext(ChatContext);
};

export const ChatProvider = ({ children }) => {
  const { currentUser } = useAuth();
  const { selectedCharacter } = useCharacter();
  const { tools, executeTool } = useTool();

  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch user's conversations when component mounts or when selected character changes
  useEffect(() => {
    if (currentUser && selectedCharacter) {
      fetchConversations();
    } else {
      setConversations([]);
      setActiveConversation(null);
      setMessages([]);
    }
  }, [currentUser, selectedCharacter]);

  // Load messages when active conversation changes
  useEffect(() => {
    if (activeConversation) {
      fetchMessages(activeConversation.id);
    } else {
      setMessages([]);
    }
  }, [activeConversation]);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      setError("");

      if (!selectedCharacter) {
        return;
      }

      // Get conversations for the selected character
      const response = await axios.get(
        `/api/v1/conversations/?character_name=${selectedCharacter.name}`
      );
      const conversationsData = response.data.conversations || [];

      setConversations(conversationsData);

      // If no conversation is active yet, activate the most recent one
      if (!activeConversation && conversationsData.length > 0) {
        setActiveConversation(conversationsData[0]);
      }
    } catch (err) {
      console.error("Failed to fetch conversations:", err);
      setError("Failed to load conversations. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      setLoading(true);
      setError("");

      // Get chat history for the conversation
      const response = await axios.get(
        `/api/v1/chat/${conversationId}/history`
      );
      const messagesData = response.data.history || [];

      setMessages(
        messagesData.map((msg, index) => ({
          id: msg.id || `msg-${index}-${Date.now()}`,
          conversationId,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp || new Date().toISOString(),
        }))
      );
    } catch (err) {
      console.error("Failed to fetch messages:", err);
      setError("Failed to load messages. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const createConversation = async (character) => {
    try {
      setError("");
      setLoading(true);

      if (!character) {
        throw new Error("No character selected");
      }

      // Generate a title based on the character
      const title = `Chat with ${character.name}`;

      // Create a new conversation with the character
      const response = await axios.post("/api/v1/conversations/", {
        character_name: character.name,
        title,
      });

      const newConversation = response.data;

      setConversations((prev) => [newConversation, ...prev]);
      setActiveConversation(newConversation);
      setMessages([]);

      return newConversation;
    } catch (err) {
      console.error("Failed to create conversation:", err);
      setError("Failed to create conversation. Please try again.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (id) => {
    try {
      setError("");
      setLoading(true);

      // Delete the conversation
      await axios.delete(`/api/v1/conversations/${id}`);

      // Update local state
      setConversations((prev) => prev.filter((conv) => conv.id !== id));

      // If the deleted conversation is currently active, set active to null or the first available
      if (activeConversation?.id === id) {
        const remainingConversations = conversations.filter(
          (conv) => conv.id !== id
        );
        if (remainingConversations.length > 0) {
          setActiveConversation(remainingConversations[0]);
        } else {
          setActiveConversation(null);
        }
      }

      return true;
    } catch (err) {
      console.error("Failed to delete conversation:", err);
      setError("Failed to delete conversation. Please try again.");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async (content, attachments = []) => {
    // Don't send empty messages
    if (!content.trim() && attachments.length === 0) return;

    try {
      setError("");

      // Create conversation if needed
      let currentConversationId = activeConversation?.id;

      if (!currentConversationId) {
        if (!selectedCharacter) {
          throw new Error("No character selected for conversation");
        }

        const newConversation = await createConversation(selectedCharacter);
        if (!newConversation) {
          throw new Error("Failed to create conversation");
        }

        currentConversationId = newConversation.id;
      }

      // Create temporary user message for UI
      const tempUserMessage = {
        id: uuidv4(),
        conversationId: currentConversationId,
        role: "user",
        content,
        attachments,
        timestamp: new Date().toISOString(),
      };

      // Optimistically add user message to UI
      setMessages((prev) => [...prev, tempUserMessage]);

      // Start typing indicator
      setIsTyping(true);

      // Send message to the API
      const response = await axios.post(
        `/api/v1/chat/${currentConversationId}`,
        {
          message: content,
        }
      );

      // Get AI response
      const aiMessage = {
        id: uuidv4(),
        conversationId: currentConversationId,
        role: "assistant",
        content: response.data.message,
        timestamp: new Date().toISOString(),
      };

      // Add AI message to UI
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);

      // Update conversation list to show this conversation at top with new timestamp
      setConversations((prev) => {
        const convIndex = prev.findIndex((c) => c.id === currentConversationId);
        if (convIndex >= 0) {
          const updatedConv = {
            ...prev[convIndex],
            updated_at: new Date().toISOString(),
          };
          const newConvs = [...prev];
          newConvs.splice(convIndex, 1);
          return [updatedConv, ...newConvs];
        }
        return prev;
      });

      return tempUserMessage;
    } catch (err) {
      console.error("Failed to send message:", err);
      setError("Failed to send message. Please try again.");
      setIsTyping(false);
      return null;
    }
  };

  const clearConversation = async () => {
    if (!activeConversation) return;

    try {
      setLoading(true);
      setError("");

      // Clear history through API
      await axios.delete(
        `/api/v1/conversations/${activeConversation.id}/history`
      );

      // Clear local messages
      setMessages([]);

      return true;
    } catch (err) {
      console.error("Failed to clear conversation history:", err);
      setError("Failed to clear conversation history. Please try again.");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const renameConversation = async (id, newTitle) => {
    try {
      setError("");
      setLoading(true);

      // Update conversation title
      const response = await axios.patch(`/api/v1/conversations/${id}`, {
        title: newTitle,
      });

      const updatedConversation = response.data;

      // Update local state
      setConversations((prev) =>
        prev.map((conv) => (conv.id === id ? updatedConversation : conv))
      );

      // Update activeConversation if it's the one being renamed
      if (activeConversation?.id === id) {
        setActiveConversation(updatedConversation);
      }

      return updatedConversation;
    } catch (err) {
      console.error("Failed to rename conversation:", err);
      setError("Failed to rename conversation. Please try again.");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = (conversation) => {
    setActiveConversation(conversation);
  };

  const value = {
    conversations,
    activeConversation,
    messages,
    isTyping,
    loading,
    error,
    fetchConversations,
    createConversation,
    deleteConversation,
    sendMessage,
    clearConversation,
    renameConversation,
    selectConversation,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
