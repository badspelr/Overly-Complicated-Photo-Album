import React, { useState, useEffect } from 'react';
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

function EditMediaModal({ open, handleClose, mediaItem, onMediaUpdated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (mediaItem) {
      setTitle(mediaItem.title);
      setDescription(mediaItem.description);
    }
  }, [mediaItem]);

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const url = mediaItem.image ? `/api/photos/${mediaItem.id}/` : `/api/videos/${mediaItem.id}/`;
    
    axios.patch(url, { title, description })
      .then(response => {
        setLoading(false);
        onMediaUpdated(response.data);
        handleClose();
      })
      .catch(error => {
        console.error("Error updating media:", error);
        setError("Failed to update media.");
        setLoading(false);
      });
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="edit-media-modal-title"
    >
      <Box sx={style}>
        <Typography id="edit-media-modal-title" variant="h6" component="h2">
          Edit Media
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="title"
            label="Title"
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
            {loading ? <CircularProgress size={24} /> : "Save Changes"}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
}

export default EditMediaModal;
