import React from "react";
import { Link } from "react-router-dom";
import { Box, Typography, Button, Container } from "@mui/material";
import { motion } from "framer-motion";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";

const NotFoundPage = () => {
  return (
    <Box className="min-h-screen flex items-center justify-center bg-background">
      <Container maxWidth="md">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mb-8"
          >
            <ErrorOutlineIcon
              className="text-primary mb-4"
              style={{ fontSize: 120 }}
            />
            <Typography variant="h2" component="h1" className="font-bold mb-2">
              404
            </Typography>
            <Typography variant="h4" className="mb-4">
              Page Not Found
            </Typography>
            <Typography variant="body1" className="text-gray-600 mb-8">
              Oops! The page you are looking for doesn't exist or has been moved.
            </Typography>
          </motion.div>

          <Link to="/" className="no-underline">
            <Button
              variant="contained"
              color="primary"
              size="large"
              className="px-6 py-3 rounded-lg font-semibold"
            >
              Back to Home
            </Button>
          </Link>
        </motion.div>
      </Container>
    </Box>
  );
};

export default NotFoundPage;
