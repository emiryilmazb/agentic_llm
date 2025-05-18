import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Grid,
  Avatar,
  IconButton,
  Snackbar,
  Alert,
  Divider,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Add as AddIcon,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router-dom";
import { motion } from "framer-motion";
import { useCharacter } from "../contexts/CharacterContext";

const CreateCharacterPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const {
    characters,
    createCharacter,
    updateCharacter,
    error,
    loading,
  } = useCharacter();

  const [formData, setFormData] = useState({
    name: "",
    avatar: "",
    description: "",
    personality: "",
    systemPrompt: "",
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  // If id is provided, load character data for editing
  useEffect(() => {
    if (id && characters) {
      const character = characters.find((char) => char.id === id);
      if (character) {
        setFormData({
          name: character.name || "",
          avatar: character.avatar || "",
          description: character.description || "",
          personality: character.personality || "",
          systemPrompt: character.systemPrompt || "",
        });
      }
    }
  }, [id, characters]);

  const validateForm = () => {
    const errors = {};

    if (!formData.name.trim()) {
      errors.name = "Name is required";
    }

    if (!formData.description.trim()) {
      errors.description = "Description is required";
    }

    if (!formData.personality.trim()) {
      errors.personality = "Personality is required";
    }

    if (!formData.systemPrompt.trim()) {
      errors.systemPrompt = "System prompt is required";
    } else if (formData.systemPrompt.trim().length < 10) {
      errors.systemPrompt = "System prompt should be more detailed";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error when field is edited
    if (formErrors[name]) {
      setFormErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      if (id) {
        // Update existing character
        await updateCharacter(id, formData);
        setSuccessMessage("Character updated successfully!");
      } else {
        // Create new character
        await createCharacter(formData);
        setSuccessMessage("Character created successfully!");
      }
      setShowSuccess(true);
      setTimeout(() => {
        navigate("/characters");
      }, 1500);
    } catch (err) {
      console.error("Failed to save character:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Avatar placeholder generator based on name
  const getAvatarPlaceholder = () => {
    if (formData.name.trim()) {
      return formData.name.charAt(0).toUpperCase();
    }
    return "C";
  };

  return (
    <Box className="p-6">
      <Box className="mb-6 flex items-center">
        <IconButton
          onClick={() => navigate("/characters")}
          className="mr-2"
          aria-label="back"
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1" className="font-bold">
          {id ? "Edit Character" : "Create Character"}
        </Typography>
      </Box>

      <Paper className="p-6 rounded-xl">
        <form onSubmit={handleSubmit}>
          <Grid container spacing={4}>
            {/* Character Basics */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" className="mb-4 font-medium">
                Basic Information
              </Typography>

              <Box className="flex items-center mb-4">
                <Avatar
                  src={formData.avatar}
                  sx={{ width: 80, height: 80 }}
                  className="mr-4 text-xl"
                >
                  {getAvatarPlaceholder()}
                </Avatar>
                <Box className="flex-1">
                  <TextField
                    label="Avatar URL"
                    name="avatar"
                    value={formData.avatar}
                    onChange={handleChange}
                    fullWidth
                    placeholder="URL to avatar image"
                    variant="outlined"
                    size="small"
                  />
                  <Typography variant="caption" className="text-gray-500 mt-1">
                    Leave empty to use a default avatar based on name
                  </Typography>
                </Box>
              </Box>

              <TextField
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                fullWidth
                required
                variant="outlined"
                margin="normal"
                error={!!formErrors.name}
                helperText={formErrors.name}
                placeholder="e.g., Technical Assistant"
              />

              <TextField
                label="Personality"
                name="personality"
                value={formData.personality}
                onChange={handleChange}
                fullWidth
                required
                variant="outlined"
                margin="normal"
                error={!!formErrors.personality}
                helperText={formErrors.personality}
                placeholder="e.g., Friendly, knowledgeable, and precise"
              />

              <TextField
                label="Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                fullWidth
                required
                multiline
                rows={3}
                variant="outlined"
                margin="normal"
                error={!!formErrors.description}
                helperText={formErrors.description}
                placeholder="Describe what this character specializes in and how it can help users"
              />
            </Grid>

            {/* Character System Prompt */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" className="mb-4 font-medium">
                System Prompt
              </Typography>
              <Typography variant="body2" className="text-gray-600 mb-3">
                The system prompt defines how the character will behave and respond. It's
                the character's personality and expertise instructions.
              </Typography>

              <TextField
                label="System Prompt"
                name="systemPrompt"
                value={formData.systemPrompt}
                onChange={handleChange}
                fullWidth
                required
                multiline
                rows={12}
                variant="outlined"
                margin="normal"
                error={!!formErrors.systemPrompt}
                helperText={
                  formErrors.systemPrompt ||
                  "Be specific about the character's knowledge, tone, and how it should respond to different types of queries."
                }
                placeholder="You are a helpful assistant specialized in technology and programming. You provide clear, accurate explanations with code examples when appropriate. You have a friendly tone and make complex topics accessible. When asked about topics outside your expertise, you politely acknowledge your limitations."
              />
            </Grid>
          </Grid>

          <Divider className="my-6" />

          <Box className="flex justify-end">
            <Button
              variant="outlined"
              color="primary"
              onClick={() => navigate("/characters")}
              className="mr-3"
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              startIcon={id ? <SaveIcon /> : <AddIcon />}
              disabled={isSubmitting}
            >
              {isSubmitting
                ? id
                  ? "Saving..."
                  : "Creating..."
                : id
                ? "Save Character"
                : "Create Character"}
            </Button>
          </Box>
        </form>
      </Paper>

      {/* Success Message */}
      <Snackbar
        open={showSuccess}
        autoHideDuration={3000}
        onClose={() => setShowSuccess(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity="success">{successMessage}</Alert>
      </Snackbar>

      {/* Error Message */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => {}}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity="error">{error}</Alert>
      </Snackbar>
    </Box>
  );
};

export default CreateCharacterPage;
