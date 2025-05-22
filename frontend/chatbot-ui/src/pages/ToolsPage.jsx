import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Button,
  Grid,
  TextField,
  InputAdornment,
  IconButton,
  CircularProgress,
  Snackbar,
  Alert,
} from "@mui/material";
import {
  Search as SearchIcon,
  Add as AddIcon,
  Clear as ClearIcon,
} from "@mui/icons-material";
import { Link } from "react-router-dom";
import { useTool } from "../contexts/ToolContext";
import ToolCard from "../components/tools/ToolCard";

const ToolsPage = () => {
  const { tools, loading, error } = useTool();
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredTools, setFilteredTools] = useState([]);
  const [showError, setShowError] = useState(false);

  // Filter tools when search term or tool list changes
  useEffect(() => {
    console.log("ToolsPage - tools değişti:", tools);
    
    if (tools && Array.isArray(tools)) {
      const filtered = tools.filter(
        (tool) =>
          tool &&
          ((tool.name && tool.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
           (tool.description && tool.description.toLowerCase().includes(searchTerm.toLowerCase())))
      );
      console.log("Filtrelenmiş araçlar:", filtered);
      setFilteredTools(filtered);
    } else {
      console.log("Tools dizisi geçerli bir dizi değil:", tools);
      setFilteredTools([]);
    }
  }, [searchTerm, tools]);

  // Show error snackbar when error state changes
  useEffect(() => {
    if (error) {
      setShowError(true);
    }
  }, [error]);

  const handleCloseError = () => {
    setShowError(false);
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const clearSearch = () => {
    setSearchTerm("");
  };

  return (
    <Box className="p-6">
      <Box className="flex flex-col md:flex-row md:justify-between md:items-center mb-8">
        <Typography variant="h4" component="h1" className="font-bold mb-4 md:mb-0">
          Tools
        </Typography>
        <Button
          component={Link}
          to="/tools/create"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
        >
          Create Tool
        </Button>
      </Box>

      {/* Search bar */}
      <Box className="mb-6">
        <TextField
          fullWidth
          placeholder="Search tools..."
          variant="outlined"
          value={searchTerm}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
            endAdornment: searchTerm && (
              <InputAdornment position="end">
                <IconButton edge="end" onClick={clearSearch} size="small">
                  <ClearIcon />
                </IconButton>
              </InputAdornment>
            ),
            className: "bg-white rounded-lg",
          }}
        />
      </Box>

      {/* Tools grid */}
      {loading ? (
        <Box className="flex justify-center items-center py-12">
          <CircularProgress />
        </Box>
      ) : filteredTools.length > 0 ? (
        <Grid container spacing={3}>
          {filteredTools.map((tool) => (
            <Grid item xs={12} sm={6} md={4} key={tool?.id || `tool-${Math.random()}`}>
              <ToolCard tool={tool} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Box className="text-center py-12 bg-gray-50 rounded-lg">
          <Typography variant="h6" className="text-gray-500 mb-2">
            {searchTerm ? "No tools match your search" : "No tools found"}
          </Typography>
          <Typography className="text-gray-500 mb-4">
            {searchTerm
              ? "Try a different search term or clear the search"
              : "Create your first tool to get started"}
          </Typography>
          {!searchTerm && (
            <Button
              component={Link}
              to="/tools/create"
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
            >
              Create Tool
            </Button>
          )}
        </Box>
      )}

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

export default ToolsPage;
