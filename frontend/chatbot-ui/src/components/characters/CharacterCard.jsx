import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Button,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Check as CheckIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useCharacter } from "../../contexts/CharacterContext";

const CharacterCard = ({ character }) => {
  const navigate = useNavigate();
  const {
    selectedCharacter,
    selectCharacter,
    deleteCharacter,
  } = useCharacter();
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const isSelected = selectedCharacter?.id === character.id;

  const handleMenuOpen = (event) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleEditClick = (event) => {
    event.stopPropagation();
    handleMenuClose();
    navigate(`/characters/edit/${character.id}`);
  };

  const handleDeleteClick = (event) => {
    event.stopPropagation();
    handleMenuClose();
    setDeleteDialogOpen(true);
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };

  const handleDeleteConfirm = async () => {
    await deleteCharacter(character.id);
    setDeleteDialogOpen(false);
  };

  const handleSelectCharacter = () => {
    selectCharacter(character);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -5 }}
    >
      <Card
        className={`h-full cursor-pointer transition-shadow hover:shadow-lg ${
          isSelected ? "border-2 border-primary" : ""
        }`}
        onClick={handleSelectCharacter}
      >
        <Box className="p-4 pb-2 flex items-center justify-between">
          <Box className="flex items-center">
            <Avatar
              src={character.avatar}
              alt={character.name}
              className="mr-3"
              sx={{ width: 56, height: 56 }}
            />
            <Box>
              <Typography variant="h6" className="font-semibold">
                {character.name}
              </Typography>
              <Typography variant="caption" className="text-gray-500">
                {character.personality}
              </Typography>
            </Box>
          </Box>
          <IconButton
            aria-label="character menu"
            onClick={handleMenuOpen}
            size="small"
          >
            <MoreVertIcon />
          </IconButton>
        </Box>

        <Divider className="mx-4" />

        <CardContent>
          <Typography variant="body2" className="text-gray-700 line-clamp-3">
            {character.description}
          </Typography>
        </CardContent>

        <CardActions className="flex justify-between">
          {isSelected ? (
            <Box className="flex items-center text-primary font-medium ml-2">
              <CheckIcon fontSize="small" className="mr-1" />
              <Typography variant="body2">Selected</Typography>
            </Box>
          ) : (
            <Button
              size="small"
              onClick={handleSelectCharacter}
              className="text-primary"
            >
              Select
            </Button>
          )}
          <Typography variant="caption" className="text-gray-500">
            Created: {new Date(character.createdAt).toLocaleDateString()}
          </Typography>
        </CardActions>

        {/* Character menu */}
        <Menu
          id={`character-menu-${character.id}`}
          anchorEl={menuAnchorEl}
          keepMounted
          open={Boolean(menuAnchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleEditClick} className="text-sm">
            <EditIcon fontSize="small" className="mr-2 text-primary" />
            Edit
          </MenuItem>
          <MenuItem onClick={handleDeleteClick} className="text-sm">
            <DeleteIcon fontSize="small" className="mr-2 text-error" />
            Delete
          </MenuItem>
        </Menu>

        {/* Delete confirmation dialog */}
        <Dialog
          open={deleteDialogOpen}
          onClose={handleDeleteCancel}
          aria-labelledby="delete-dialog-title"
        >
          <DialogTitle id="delete-dialog-title">
            Delete Character
          </DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete the character "{character.name}"?
              This action cannot be undone.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDeleteCancel} color="primary">
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConfirm}
              color="error"
              variant="contained"
            >
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Card>
    </motion.div>
  );
};

export default CharacterCard;
