import React, { useState, useRef } from "react";
import {
  Box,
  TextField,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  EmojiEmotions as EmojiIcon,
  Code as CodeIcon,
  Build as BuildIcon,
  MoreVert as MoreVertIcon,
} from "@mui/icons-material";
import { motion } from "framer-motion";
import { useChat } from "../../contexts/ChatContext";
import { useTool } from "../../contexts/ToolContext";

const ChatInput = () => {
  const { sendMessage, isTyping } = useChat();
  const { tools } = useTool();
  const [message, setMessage] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [isFocused, setIsFocused] = useState(false);
  const [toolMenuAnchorEl, setToolMenuAnchorEl] = useState(null);
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolDialogOpen, setToolDialogOpen] = useState(false);
  const [toolParams, setToolParams] = useState({});
  const fileInputRef = useRef(null);

  const handleSendMessage = (e) => {
    e?.preventDefault();
    if (message.trim() || attachments.length > 0) {
      sendMessage(message, attachments);
      setMessage("");
      setAttachments([]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
      setAttachments((prevAttachments) => [...prevAttachments, ...files]);
    }
  };

  const handleRemoveAttachment = (index) => {
    setAttachments((prevAttachments) =>
      prevAttachments.filter((_, i) => i !== index)
    );
  };

  const handleToolMenuOpen = (event) => {
    setToolMenuAnchorEl(event.currentTarget);
  };

  const handleToolMenuClose = () => {
    setToolMenuAnchorEl(null);
  };

  const handleToolSelect = (tool) => {
    setSelectedTool(tool);
    setToolParams({});
    handleToolMenuClose();
    setToolDialogOpen(true);
  };

  const handleToolDialogClose = () => {
    setToolDialogOpen(false);
    setSelectedTool(null);
  };

  const handleToolParamChange = (paramName, value) => {
    setToolParams((prev) => ({
      ...prev,
      [paramName]: value,
    }));
  };

  const handleToolUse = () => {
    // Format tool usage as a message
    const paramText = Object.entries(toolParams)
      .map(([key, value]) => `${key}: ${value}`)
      .join(", ");
    
    const toolMessage = `use ${selectedTool.name} with parameters ${paramText}`;
    setMessage(toolMessage);
    setToolDialogOpen(false);
    // Don't send immediately, let the user review and edit if needed
  };

  const insertCodeBlock = () => {
    const codeBlockTemplate = "```\n// Your code here\n```";
    setMessage((prev) => {
      if (prev.endsWith("\n") || prev === "") {
        return prev + codeBlockTemplate;
      } else {
        return prev + "\n" + codeBlockTemplate;
      }
    });
  };

  return (
    <Box>
      <form onSubmit={handleSendMessage}>
        {/* Attachments preview */}
        {attachments.length > 0 && (
          <Box className="flex flex-wrap gap-2 mb-2">
            {attachments.map((file, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="relative bg-gray-100 rounded-md p-2"
              >
                <Box className="flex items-center">
                  <AttachFileIcon fontSize="small" className="mr-1" />
                  <Typography variant="caption" noWrap className="max-w-[150px]">
                    {file.name}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => handleRemoveAttachment(index)}
                    className="ml-1 text-gray-500 hover:text-error"
                  >
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </Box>
              </motion.div>
            ))}
          </Box>
        )}

        {/* Input area */}
        <Box
          className={`flex items-end border rounded-xl transition-shadow p-2 ${
            isFocused ? "border-primary shadow-md" : "border-gray-300"
          }`}
        >
          <TextField
            multiline
            maxRows={5}
            variant="standard"
            placeholder="Type a message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            fullWidth
            InputProps={{
              disableUnderline: true,
              className: "px-2 py-1",
            }}
            disabled={isTyping}
          />

          {/* Action buttons */}
          <Box className="flex items-center ml-2">
            <Tooltip title="Attach file">
              <IconButton
                onClick={handleAttachmentClick}
                className="text-gray-500"
                disabled={isTyping}
              >
                <AttachFileIcon />
              </IconButton>
            </Tooltip>
            <input
              type="file"
              multiple
              ref={fileInputRef}
              style={{ display: "none" }}
              onChange={handleFileChange}
            />

            <Tooltip title="Insert code block">
              <IconButton
                onClick={insertCodeBlock}
                className="text-gray-500"
                disabled={isTyping}
              >
                <CodeIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="Use tool">
              <IconButton
                onClick={handleToolMenuOpen}
                className="text-gray-500"
                disabled={isTyping || tools.length === 0}
              >
                <BuildIcon />
              </IconButton>
            </Tooltip>

            <Menu
              anchorEl={toolMenuAnchorEl}
              open={Boolean(toolMenuAnchorEl)}
              onClose={handleToolMenuClose}
              anchorOrigin={{
                vertical: "top",
                horizontal: "center",
              }}
              transformOrigin={{
                vertical: "bottom",
                horizontal: "center",
              }}
            >
              {tools.length > 0 ? (
                tools.map((tool) => (
                  <MenuItem
                    key={tool.id}
                    onClick={() => handleToolSelect(tool)}
                    className="text-sm py-2"
                  >
                    {tool.name}
                  </MenuItem>
                ))
              ) : (
                <MenuItem disabled>No tools available</MenuItem>
              )}
            </Menu>

            <Tooltip title="Send message">
              <IconButton
                type="submit"
                color="primary"
                disabled={
                  isTyping || (message.trim() === "" && attachments.length === 0)
                }
                className={message.trim() || attachments.length > 0 ? "" : "opacity-50"}
              >
                <SendIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </form>

      {/* Tool parameter dialog */}
      <Dialog open={toolDialogOpen} onClose={handleToolDialogClose}>
        <DialogTitle>
          Use {selectedTool?.name || "Tool"}
          <Typography variant="body2" color="textSecondary">
            {selectedTool?.description}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedTool?.parameters?.map((param) => (
            <Box key={param.name} className="mb-4">
              <TextField
                label={param.name}
                fullWidth
                margin="dense"
                required={param.required}
                helperText={param.description}
                placeholder={param.defaultValue !== undefined ? String(param.defaultValue) : ""}
                value={toolParams[param.name] || ""}
                onChange={(e) =>
                  handleToolParamChange(param.name, e.target.value)
                }
              />
            </Box>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleToolDialogClose}>Cancel</Button>
          <Button
            onClick={handleToolUse}
            variant="contained"
            color="primary"
            disabled={
              selectedTool?.parameters
                ?.filter((p) => p.required)
                .some((p) => !toolParams[p.name])
            }
          >
            Use Tool
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatInput;
