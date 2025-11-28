import React, { useState } from 'react';
import axios from '../api/axios';
import { Modal, Box, Typography, TextField, Button, CircularProgress } from '@mui/material';

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: 400,
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};

function CreateAlbumModal({ open, handleClose, onAlbumCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    // Get CSRF token from cookie
    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];

    axios.post('/api/albums/', { title, description }, {
      headers: {
        'X-CSRFToken': csrftoken
      }
    })
      .then(response => {
        setLoading(false);
        onAlbumCreated(response.data);
        handleClose();
      })
      .catch(error => {
        console.error("Error creating album:", error);
        setError("Failed to create album.");
        setLoading(false);
      });
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="create-album-modal-title"
    >
      <Box sx={style}>
        <Typography id="create-album-modal-title" variant="h6" component="h2">
          Create New Album
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="title"
            label="Album Title"
            name="title"
            autoFocus
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <TextField
            margin="normal"
            fullWidth
            id="description"
            label="Description (Optional)"
            name="description"
            multiline
            rows={4}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          {error && <Typography color="error">{error}</Typography>}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Create Album"}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
}

export default CreateAlbumModal;
