import React, { useEffect, useRef } from "react";
import { Box, Typography, Avatar } from "@mui/material";
import { Person as PersonIcon } from "@mui/icons-material";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import { useChat } from "../../contexts/ChatContext";
import { useCharacter } from "../../contexts/CharacterContext";

const MessageList = () => {
  const { messages, isTyping } = useChat();
  const { selectedCharacter } = useCharacter();
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Format timestamp
  const formatTime = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    } catch (e) {
      return "";
    }
  };

  return (
    <Box>
      {messages.length === 0 ? (
        <Box className="text-center py-8">
          <Typography className="text-gray-500">
            Start a conversation by sending a message below.
          </Typography>
        </Box>
      ) : (
        messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            } mb-4`}
          >
            {message.role === "assistant" && (
              <Avatar
                src={selectedCharacter?.avatar || ""}
                className="mt-1 mr-2"
                alt={selectedCharacter?.name || "AI"}
              >
                {!selectedCharacter?.avatar && <PersonIcon />}
              </Avatar>
            )}

            <Box
              className={`message-bubble ${
                message.role === "user"
                  ? "message-bubble-user"
                  : "message-bubble-bot"
              } max-w-[80%]`}
            >
              {message.role === "user" ? (
                <Typography>{message.content}</Typography>
              ) : (
                <>
                  <ReactMarkdown
                    className="prose prose-sm max-w-none"
                    remarkPlugins={[remarkGfm]}
                    components={{
                      code({ node, inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        return !inline && match ? (
                          <SyntaxHighlighter
                            style={atomDark}
                            language={match[1]}
                            PreTag="div"
                            {...props}
                          >
                            {String(children).replace(/\n$/, "")}
                          </SyntaxHighlighter>
                        ) : (
                          <code className={className} {...props}>
                            {children}
                          </code>
                        );
                      },
                      p: ({ node, ...props }) => (
                        <p className="mb-2 last:mb-0" {...props} />
                      ),
                      ul: ({ node, ...props }) => (
                        <ul className="list-disc pl-5 mb-2" {...props} />
                      ),
                      ol: ({ node, ...props }) => (
                        <ol className="list-decimal pl-5 mb-2" {...props} />
                      ),
                      li: ({ node, ...props }) => (
                        <li className="mb-1" {...props} />
                      ),
                      a: ({ node, children, ...props }) => (
                        <a className="text-blue-600 hover:underline" {...props}>{children}</a>
                      ),
                      h1: ({ node, children, ...props }) => (
                        <h1 className="text-xl font-bold my-4" {...props}>{children}</h1>
                      ),
                      h2: ({ node, children, ...props }) => (
                        <h2 className="text-lg font-bold my-3" {...props}>{children}</h2>
                      ),
                      h3: ({ node, children, ...props }) => (
                        <h3 className="text-md font-bold my-2" {...props}>{children}</h3>
                      ),
                      blockquote: ({ node, ...props }) => (
                        <blockquote
                          className="border-l-4 border-gray-300 pl-4 py-1 my-2 text-gray-700 italic"
                          {...props}
                        />
                      ),
                      table: ({ node, ...props }) => (
                        <div className="overflow-x-auto my-4">
                          <table
                            className="border-collapse border border-gray-300 min-w-full"
                            {...props}
                          />
                        </div>
                      ),
                      th: ({ node, ...props }) => (
                        <th
                          className="border border-gray-300 px-4 py-2 bg-gray-100 font-medium"
                          {...props}
                        />
                      ),
                      td: ({ node, ...props }) => (
                        <td
                          className="border border-gray-300 px-4 py-2"
                          {...props}
                        />
                      ),
                      hr: ({ node, ...props }) => (
                        <hr className="my-4 border-t border-gray-300" {...props} />
                      ),
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                  
                  {message.data && (
                    <Box className="mt-2 p-2 bg-gray-100 rounded-md">
                      {/* Agentic yanıtlar için ek veri gösterimi */}
                      <Typography variant="caption" className="font-semibold">
                        {message.data.type}
                      </Typography>
                      <Typography variant="body2">
                        {message.data.display_text}
                      </Typography>
                    </Box>
                  )}
                </>
              )}

              <Typography
                variant="caption"
                className={`block text-right mt-1 ${
                  message.role === "user" ? "text-gray-200" : "text-gray-500"
                }`}
              >
                {formatTime(message.timestamp)}
              </Typography>
            </Box>

            {message.role === "user" && (
              <Avatar className="mt-1 ml-2 bg-primary">
                {/* Get first letter of user's name */}
                U
              </Avatar>
            )}
          </motion.div>
        ))
      )}

      {/* Typing indicator */}
      {isTyping && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-start mb-4"
        >
          <Avatar
            src={selectedCharacter?.avatar || ""}
            className="mt-1 mr-2"
            alt={selectedCharacter?.name || "AI"}
          >
            {!selectedCharacter?.avatar && <PersonIcon />}
          </Avatar>
          <Box className="message-bubble message-bubble-bot py-3 px-4">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </Box>
        </motion.div>
      )}

      {/* Invisible element to scroll to */}
      <div ref={messagesEndRef} />
    </Box>
  );
};

export default MessageList;
