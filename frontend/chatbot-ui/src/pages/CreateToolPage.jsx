import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  TextField,
  Paper,
  Grid,
  IconButton,
  Snackbar,
  Alert,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Card,
  CardContent,
  Tooltip,
} from "@mui/material";
import {
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIndicatorIcon,
} from "@mui/icons-material";
import { useNavigate, useParams } from "react-router-dom";
import { useTool } from "../contexts/ToolContext";

const PARAMETER_TYPES = ["string", "number", "boolean", "object", "array"];
const ICON_OPTIONS = ["build", "cloud", "search", "weather"];

const CreateToolPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { tools, createTool, updateTool, error } = useTool();

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    icon: "build",
    endpoint: "",
    parameters: [],
  });
  const [formErrors, setFormErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [parameterErrors, setParameterErrors] = useState([]);
  const [newParameter, setNewParameter] = useState({
    name: "",
    type: "string",
    description: "",
    required: true,
    defaultValue: "",
  });

  // If id is provided, load tool data for editing
  useEffect(() => {
    if (id && tools) {
      const tool = tools.find((t) => t.id === id);
      if (tool) {
        setFormData({
          name: tool.name || "",
          description: tool.description || "",
          icon: tool.icon || "build",
          endpoint: tool.endpoint || "",
          parameters: tool.parameters || [],
        });
      }
    }
  }, [id, tools]);

  const validateForm = () => {
    const errors = {};

    if (!formData.name.trim()) {
      errors.name = "Name is required";
    }

    if (!formData.description.trim()) {
      errors.description = "Description is required";
    }

    if (!formData.endpoint.trim()) {
      errors.endpoint = "Endpoint is required";
    } else if (
      !formData.endpoint.startsWith("/") &&
      !formData.endpoint.startsWith("http")
    ) {
      errors.endpoint = "Endpoint must start with '/' or 'http'";
    }

    // Validate parameters
    const paramErrors = formData.parameters.map((param) => {
      const pErrors = {};
      if (!param.name.trim()) {
        pErrors.name = "Name is required";
      }
      if (!param.description.trim()) {
        pErrors.description = "Description is required";
      }
      return pErrors;
    });

    if (paramErrors.some((err) => Object.keys(err).length > 0)) {
      errors.parameters = "One or more parameters have errors";
      setParameterErrors(paramErrors);
    } else {
      setParameterErrors([]);
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

  const handleNewParameterChange = (e) => {
    const { name, value } = e.target;
    if (name === "required") {
      setNewParameter((prev) => ({
        ...prev,
        [name]: e.target.checked,
      }));
    } else {
      setNewParameter((prev) => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleAddParameter = () => {
    if (!newParameter.name.trim() || !newParameter.description.trim()) {
      return;
    }

    setFormData((prev) => ({
      ...prev,
      parameters: [...prev.parameters, { ...newParameter }],
    }));

    setNewParameter({
      name: "",
      type: "string",
      description: "",
      required: true,
      defaultValue: "",
    });
  };

  const handleUpdateParameter = (index, field, value) => {
    setFormData((prev) => {
      const updatedParameters = [...prev.parameters];
      updatedParameters[index] = {
        ...updatedParameters[index],
        [field]: value,
      };
      return {
        ...prev,
        parameters: updatedParameters,
      };
    });

    // Clear errors for this parameter
    if (parameterErrors[index] && parameterErrors[index][field]) {
      const updatedErrors = [...parameterErrors];
      updatedErrors[index] = {
        ...updatedErrors[index],
        [field]: undefined,
      };
      setParameterErrors(updatedErrors);
    }
  };

  const handleDeleteParameter = (index) => {
    setFormData((prev) => {
      const updatedParameters = [...prev.parameters];
      updatedParameters.splice(index, 1);
      return {
        ...prev,
        parameters: updatedParameters,
      };
    });

    // Remove errors for this parameter
    if (parameterErrors.length > index) {
      const updatedErrors = [...parameterErrors];
      updatedErrors.splice(index, 1);
      setParameterErrors(updatedErrors);
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
        // Update existing tool
        await updateTool(id, formData);
        setSuccessMessage("Tool updated successfully!");
      } else {
        // Create new tool
        await createTool(formData);
        setSuccessMessage("Tool created successfully!");
      }
      setShowSuccess(true);
      setTimeout(() => {
        navigate("/tools");
      }, 1500);
    } catch (err) {
      console.error("Failed to save tool:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Box className="p-6">
      <Box className="mb-6 flex items-center">
        <IconButton
          onClick={() => navigate("/tools")}
          className="mr-2"
          aria-label="back"
        >
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h4" component="h1" className="font-bold">
          {id ? "Edit Tool" : "Create Tool"}
        </Typography>
      </Box>

      <Paper className="p-6 rounded-xl">
        <form onSubmit={handleSubmit}>
          <Grid container spacing={4}>
            {/* Tool Basics */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" className="mb-4 font-medium">
                Basic Information
              </Typography>

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
                placeholder="e.g., Weather Tool"
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
                placeholder="Describe what this tool does and how it can be used in conversations"
              />

              <FormControl fullWidth margin="normal">
                <InputLabel id="icon-select-label">Icon</InputLabel>
                <Select
                  labelId="icon-select-label"
                  id="icon-select"
                  name="icon"
                  value={formData.icon}
                  label="Icon"
                  onChange={handleChange}
                >
                  {ICON_OPTIONS.map((icon) => (
                    <MenuItem key={icon} value={icon}>
                      {icon.charAt(0).toUpperCase() + icon.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
                <FormHelperText>
                  Select an icon that represents this tool's function
                </FormHelperText>
              </FormControl>

              <TextField
                label="Endpoint"
                name="endpoint"
                value={formData.endpoint}
                onChange={handleChange}
                fullWidth
                required
                variant="outlined"
                margin="normal"
                error={!!formErrors.endpoint}
                helperText={
                  formErrors.endpoint ||
                  "The API endpoint for this tool (e.g., /api/tools/weather)"
                }
                placeholder="/api/tools/example"
              />
            </Grid>

            {/* Tool Parameters */}
            <Grid item xs={12} md={6}>
              <Typography variant="h6" className="mb-4 font-medium">
                Parameters
              </Typography>
              <Typography variant="body2" className="text-gray-600 mb-3">
                Define the parameters that this tool accepts. These will be shown to the
                user when they want to use this tool in a conversation.
              </Typography>

              {formData.parameters.length > 0 ? (
                <Box className="mb-4 space-y-4">
                  {formData.parameters.map((param, index) => (
                    <Card
                      key={index}
                      variant="outlined"
                      className="border-gray-300"
                    >
                      <CardContent className="p-4">
                        <Box className="flex justify-between items-center mb-2">
                          <Box className="flex items-center">
                            <DragIndicatorIcon
                              className="text-gray-400 mr-2"
                              fontSize="small"
                            />
                            <Typography variant="subtitle1" className="font-medium">
                              Parameter {index + 1}
                            </Typography>
                          </Box>
                          <Tooltip title="Delete parameter">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleDeleteParameter(index)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>

                        <Grid container spacing={2}>
                          <Grid item xs={7}>
                            <TextField
                              label="Name"
                              fullWidth
                              value={param.name}
                              onChange={(e) =>
                                handleUpdateParameter(index, "name", e.target.value)
                              }
                              error={
                                parameterErrors[index] &&
                                !!parameterErrors[index].name
                              }
                              helperText={
                                parameterErrors[index]
                                  ? parameterErrors[index].name
                                  : ""
                              }
                              size="small"
                              margin="dense"
                            />
                          </Grid>
                          <Grid item xs={5}>
                            <FormControl fullWidth margin="dense" size="small">
                              <InputLabel id={`type-label-${index}`}>
                                Type
                              </InputLabel>
                              <Select
                                labelId={`type-label-${index}`}
                                value={param.type}
                                label="Type"
                                onChange={(e) =>
                                  handleUpdateParameter(
                                    index,
                                    "type",
                                    e.target.value
                                  )
                                }
                              >
                                {PARAMETER_TYPES.map((type) => (
                                  <MenuItem key={type} value={type}>
                                    {type}
                                  </MenuItem>
                                ))}
                              </Select>
                            </FormControl>
                          </Grid>
                          <Grid item xs={12}>
                            <TextField
                              label="Description"
                              fullWidth
                              value={param.description}
                              onChange={(e) =>
                                handleUpdateParameter(
                                  index,
                                  "description",
                                  e.target.value
                                )
                              }
                              error={
                                parameterErrors[index] &&
                                !!parameterErrors[index].description
                              }
                              helperText={
                                parameterErrors[index]
                                  ? parameterErrors[index].description
                                  : ""
                              }
                              size="small"
                              margin="dense"
                            />
                          </Grid>
                          <Grid item xs={6}>
                            <TextField
                              label="Default Value (optional)"
                              fullWidth
                              value={param.defaultValue || ""}
                              onChange={(e) =>
                                handleUpdateParameter(
                                  index,
                                  "defaultValue",
                                  e.target.value
                                )
                              }
                              size="small"
                              margin="dense"
                            />
                          </Grid>
                          <Grid item xs={6}>
                            <FormControl fullWidth margin="dense" size="small">
                              <InputLabel id={`required-label-${index}`}>
                                Required
                              </InputLabel>
                              <Select
                                labelId={`required-label-${index}`}
                                value={param.required}
                                label="Required"
                                onChange={(e) =>
                                  handleUpdateParameter(
                                    index,
                                    "required",
                                    e.target.value
                                  )
                                }
                              >
                                <MenuItem value={true}>Yes</MenuItem>
                                <MenuItem value={false}>No</MenuItem>
                              </Select>
                            </FormControl>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              ) : (
                <Box className="bg-gray-50 p-4 rounded-lg text-center mb-4">
                  <Typography variant="body2" className="text-gray-500">
                    No parameters added yet. Add parameters to define what input
                    this tool needs.
                  </Typography>
                </Box>
              )}

              {formErrors.parameters && (
                <Alert severity="error" className="mb-4">
                  {formErrors.parameters}
                </Alert>
              )}

              {/* Add new parameter form */}
              <Card className="border-dashed border-2 border-gray-300 mt-4">
                <CardContent>
                  <Typography variant="subtitle1" className="font-medium mb-2">
                    Add New Parameter
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={7}>
                      <TextField
                        label="Name"
                        fullWidth
                        value={newParameter.name}
                        onChange={handleNewParameterChange}
                        name="name"
                        size="small"
                        margin="dense"
                        placeholder="e.g., location"
                      />
                    </Grid>
                    <Grid item xs={5}>
                      <FormControl fullWidth margin="dense" size="small">
                        <InputLabel id="new-type-label">Type</InputLabel>
                        <Select
                          labelId="new-type-label"
                          value={newParameter.type}
                          label="Type"
                          name="type"
                          onChange={handleNewParameterChange}
                        >
                          {PARAMETER_TYPES.map((type) => (
                            <MenuItem key={type} value={type}>
                              {type}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <TextField
                        label="Description"
                        fullWidth
                        value={newParameter.description}
                        onChange={handleNewParameterChange}
                        name="description"
                        size="small"
                        margin="dense"
                        placeholder="Explain what this parameter is for"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <TextField
                        label="Default Value (optional)"
                        fullWidth
                        value={newParameter.defaultValue}
                        onChange={handleNewParameterChange}
                        name="defaultValue"
                        size="small"
                        margin="dense"
                      />
                    </Grid>
                    <Grid item xs={6}>
                      <FormControl fullWidth margin="dense" size="small">
                        <InputLabel id="new-required-label">
                          Required
                        </InputLabel>
                        <Select
                          labelId="new-required-label"
                          value={newParameter.required}
                          label="Required"
                          name="required"
                          onChange={handleNewParameterChange}
                        >
                          <MenuItem value={true}>Yes</MenuItem>
                          <MenuItem value={false}>No</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        variant="outlined"
                        color="primary"
                        onClick={handleAddParameter}
                        startIcon={<AddIcon />}
                        disabled={
                          !newParameter.name || !newParameter.description
                        }
                        fullWidth
                      >
                        Add Parameter
                      </Button>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Divider className="my-6" />

          <Box className="flex justify-end">
            <Button
              variant="outlined"
              color="primary"
              onClick={() => navigate("/tools")}
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
                ? "Save Tool"
                : "Create Tool"}
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

export default CreateToolPage;
