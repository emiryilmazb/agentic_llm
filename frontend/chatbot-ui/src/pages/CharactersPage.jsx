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
import { useCharacter } from "../contexts/CharacterContext";
import CharacterCard from "../components/characters/CharacterCard";

const CharactersPage = () => {
  const { characters, loading, error } = useCharacter();
  const [searchTerm, setSearchTerm] = useState("");
  const [filteredCharacters, setFilteredCharacters] = useState([]);
  const [showError, setShowError] = useState(false);

  // Filter characters when search term or character list changes
  useEffect(() => {
    console.log("CharactersPage - characters değişti:", characters);
    
    if (characters && Array.isArray(characters)) {
      const filtered = characters.filter(
        (character) =>
          character &&
          ((character.name && character.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
           (character.description && character.description.toLowerCase().includes(searchTerm.toLowerCase())))
      );
      console.log("Filtrelenmiş karakterler:", filtered);
      setFilteredCharacters(filtered);
    } else {
      console.log("Characters dizisi geçerli bir dizi değil:", characters);
      // Ensure filteredCharacters is always an array
      setFilteredCharacters([]);
    }
  }, [searchTerm, characters]);

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
          Characters
        </Typography>
        <Button
          component={Link}
          to="/characters/create"
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
        >
          Create Character
        </Button>
      </Box>

      {/* Search bar */}
      <Box className="mb-6">
        <TextField
          fullWidth
          placeholder="Search characters..."
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

      {/* Characters grid */}
      {loading ? (
        <Box className="flex justify-center items-center py-12">
          <CircularProgress />
        </Box>
      ) : filteredCharacters.length > 0 ? (
        <Grid container spacing={3}>
          {filteredCharacters.map((character) => (
            <Grid item xs={12} sm={6} md={4} key={character?.id || `character-${Math.random()}`}>
              <CharacterCard character={character} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <Box className="text-center py-12 bg-gray-50 rounded-lg">
          <Typography variant="h6" className="text-gray-500 mb-2">
            {searchTerm
              ? "No characters match your search"
              : "No characters found"}
          </Typography>
          <Typography className="text-gray-500 mb-4">
            {searchTerm
              ? "Try a different search term or clear the search"
              : "Create your first character to get started"}
          </Typography>
          {!searchTerm && (
            <Button
              component={Link}
              to="/characters/create"
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
            >
              Create Character
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

export default CharactersPage;
