import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import { Modal, Box, Typography, TextField, Button, CircularProgress, Select, MenuItem, FormControl, InputLabel } from '@mui/material';

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

function InviteUserModal({ open, handleClose, onUserInvited }) {
  const [email, setEmail] = useState('');
  const [albumId, setAlbumId] = useState('');
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open) {
      axios.get('/api/albums/')
        .then(response => {
          setAlbums(response.data.results);
        })
        .catch(error => {
          console.error("Error fetching albums:", error);
        });
    }
  }, [open]);

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const csrftoken = document.cookie.split('; ').find(row => row.startsWith('csrftoken=')).split('=')[1];

    axios.post(`/api/albums/${albumId}/add_viewer/`, { email }, {
      headers: {
        'X-CSRFToken': csrftoken
      }
    })
      .then(response => {
        setLoading(false);
        onUserInvited(response.data);
        handleClose();
      })
      .catch(error => {
        console.error("Error inviting user:", error);
        setError("Failed to invite user.");
        setLoading(false);
      });
  };

  return (
    <Modal
      open={open}
      onClose={handleClose}
      aria-labelledby="invite-user-modal-title"
    >
      <Box sx={style}>
        <Typography id="invite-user-modal-title" variant="h6" component="h2">
          Invite User to Album
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="User Email"
            name="email"
            type="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel id="album-select-label">Select Album</InputLabel>
            <Select
              labelId="album-select-label"
              id="album-select"
              value={albumId}
              label="Select Album"
              onChange={(e) => setAlbumId(e.target.value)}
              required
            >
              {albums.map(album => (
                <MenuItem key={album.id} value={album.id}>{album.title}</MenuItem>
              ))}
            </Select>
          </FormControl>
          {error && <Typography color="error">{error}</Typography>}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : "Invite User"}
          </Button>
        </Box>
      </Box>
    </Modal>
  );
}

export default InviteUserModal;
