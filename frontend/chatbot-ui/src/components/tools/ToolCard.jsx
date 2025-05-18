import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  CardActions,
  Typography,
  IconButton,
  Menu,
  MenuItem,
  Chip,
  Button,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Tooltip,
} from "@mui/material";
import {
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Build as BuildIcon,
  Info as InfoIcon,
  Cloud as CloudIcon,
  Search as SearchIcon,
} from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useTool } from "../../contexts/ToolContext";

// Icon mapping for different tool types
const iconMap = {
  cloud: <CloudIcon />,
  weather: <CloudIcon />,
  search: <SearchIcon />,
  default: <BuildIcon />,
};

const ToolCard = ({ tool }) => {
  const navigate = useNavigate();
  const { deleteTool } = useTool();
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [infoDialogOpen, setInfoDialogOpen] = useState(false);

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
    navigate(`/tools/edit/${tool.id}`);
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
    await deleteTool(tool.id);
    setDeleteDialogOpen(false);
  };

  const handleInfoOpen = (event) => {
    event.stopPropagation();
    setInfoDialogOpen(true);
  };

  const handleInfoClose = () => {
    setInfoDialogOpen(false);
  };

  // Get icon based on tool type
  const getToolIcon = () => {
    if (tool.icon && iconMap[tool.icon.toLowerCase()]) {
      return iconMap[tool.icon.toLowerCase()];
    }
    return iconMap.default;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ y: -5 }}
    >
      <Card className="h-full cursor-pointer transition-shadow hover:shadow-lg">
        <Box className="p-4 pb-2 flex items-center justify-between">
          <Box className="flex items-center">
            <Box
              className="mr-3 p-2 rounded-full bg-primary-light bg-opacity-20 text-primary"
              sx={{ width: 48, height: 48, display: "flex", alignItems: "center", justifyContent: "center" }}
            >
              {getToolIcon()}
            </Box>
            <Box>
              <Typography variant="h6" className="font-semibold">
                {tool.name}
              </Typography>
              <Chip
                label={`${tool.parameters.length} ${
                  tool.parameters.length === 1 ? "Parameter" : "Parameters"
                }`}
                size="small"
                className="bg-gray-100 text-gray-700"
              />
            </Box>
          </Box>
          <IconButton
            aria-label="tool menu"
            onClick={handleMenuOpen}
            size="small"
          >
            <MoreVertIcon />
          </IconButton>
        </Box>

        <Divider className="mx-4" />

        <CardContent>
          <Typography variant="body2" className="text-gray-700 line-clamp-3">
            {tool.description}
          </Typography>
        </CardContent>

        <CardActions className="flex justify-between">
          <Tooltip title="Show tool details">
            <Button
              size="small"
              onClick={handleInfoOpen}
              className="text-primary"
              startIcon={<InfoIcon fontSize="small" />}
            >
              Details
            </Button>
          </Tooltip>
          <Typography variant="caption" className="text-gray-500">
            Endpoint: {tool.endpoint.split('/').pop()}
          </Typography>
        </CardActions>

        {/* Tool menu */}
        <Menu
          id={`tool-menu-${tool.id}`}
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
          <DialogTitle id="delete-dialog-title">Delete Tool</DialogTitle>
          <DialogContent>
            <DialogContentText>
              Are you sure you want to delete the tool "{tool.name}"? This
              action cannot be undone.
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

        {/* Tool info dialog */}
        <Dialog
          open={infoDialogOpen}
          onClose={handleInfoClose}
          aria-labelledby="info-dialog-title"
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle id="info-dialog-title">{tool.name}</DialogTitle>
          <DialogContent>
            <Typography variant="body1" className="mb-4">
              {tool.description}
            </Typography>

            <Typography variant="subtitle1" className="font-semibold mt-4 mb-2">
              Parameters:
            </Typography>
            {tool.parameters.length === 0 ? (
              <Typography variant="body2" className="text-gray-500 italic">
                No parameters required
              </Typography>
            ) : (
              tool.parameters.map((param, index) => (
                <Box key={index} className="mb-3 p-3 bg-gray-50 rounded-md">
                  <Box className="flex justify-between items-center mb-1">
                    <Typography variant="subtitle2" className="font-semibold">
                      {param.name}
                      {param.required && (
                        <span className="text-error-light ml-1">*</span>
                      )}
                    </Typography>
                    <Chip
                      label={param.type}
                      size="small"
                      className="bg-primary-light bg-opacity-20 text-primary"
                    />
                  </Box>
                  <Typography variant="body2" className="text-gray-700">
                    {param.description}
                  </Typography>
                  {param.defaultValue !== undefined && (
                    <Typography
                      variant="caption"
                      className="text-gray-500 block mt-1"
                    >
                      Default: {String(param.defaultValue)}
                    </Typography>
                  )}
                </Box>
              ))
            )}

            <Typography variant="subtitle1" className="font-semibold mt-4 mb-2">
              Endpoint:
            </Typography>
            <Typography variant="body2" className="text-gray-700 font-mono p-2 bg-gray-50 rounded">
              {tool.endpoint}
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleInfoClose} color="primary">
              Close
            </Button>
            <Button
              onClick={handleEditClick}
              color="primary"
              variant="contained"
              startIcon={<EditIcon />}
            >
              Edit Tool
            </Button>
          </DialogActions>
        </Dialog>
      </Card>
    </motion.div>
  );
};

export default ToolCard;
