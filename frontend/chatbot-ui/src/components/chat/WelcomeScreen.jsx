import React from "react";
import { Box, Typography, Button, Paper } from "@mui/material";
import { motion } from "framer-motion";
import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutline";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import { Link } from "react-router-dom";
import { useCharacter } from "../../contexts/CharacterContext";

const WelcomeScreen = ({ onStartNewChat, hasCharacters }) => {
  const { selectedCharacter } = useCharacter();

  return (
    <Box className="h-full flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl w-full"
      >
        <Paper className="p-8 rounded-xl shadow-chat">
          <Box className="text-center">
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <ChatBubbleOutlineIcon
                className="text-primary mb-4"
                style={{ fontSize: 60 }}
              />
            </motion.div>
            <Typography variant="h4" className="font-bold mb-2">
              Welcome to AI Chatbot
            </Typography>
            <Typography className="text-gray-600 mb-8">
              Engage in conversations with different AI characters and use custom tools
            </Typography>

            <Box className="flex flex-col space-y-6 mb-8">
              <Feature
                title="Multiple Characters"
                description="Chat with different AI personalities, each with their own expertise and style"
                delay={0.3}
              />
              <Feature
                title="Dynamic Tools"
                description="Enhance conversations with specialized tools for information retrieval, data analysis, and more"
                delay={0.4}
              />
              <Feature
                title="Custom Creation"
                description="Create your own characters and tools to build the perfect AI assistant for your needs"
                delay={0.5}
              />
            </Box>

            <Box className="flex flex-col md:flex-row justify-center gap-4">
              {selectedCharacter ? (
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  startIcon={<ChatBubbleOutlineIcon />}
                  onClick={onStartNewChat}
                  className="px-6 py-3"
                >
                  Start Chatting with {selectedCharacter.name}
                </Button>
              ) : (
                <Button
                  component={Link}
                  to="/characters"
                  variant="contained"
                  color="primary"
                  size="large"
                  startIcon={<PersonAddIcon />}
                  className="px-6 py-3"
                >
                  {hasCharacters ? "Select a Character" : "Create a Character"}
                </Button>
              )}
            </Box>
          </Box>
        </Paper>
      </motion.div>
    </Box>
  );
};

const Feature = ({ title, description, delay }) => (
  <motion.div
    initial={{ opacity: 0, x: -20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay, duration: 0.5 }}
    className="text-center"
  >
    <Typography variant="h6" className="font-semibold mb-1">
      {title}
    </Typography>
    <Typography variant="body2" className="text-gray-600">
      {description}
    </Typography>
  </motion.div>
);

export default WelcomeScreen;
