import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import { Box, Typography, TextField, Button, CircularProgress, Alert, Paper } from '@mui/material';

function ProfilePage() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    axios.get('/api/user/me/')
      .then(response => {
        setUser(response.data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load user profile.");
        setLoading(false);
      });
  }, []);

  const handleChange = (event) => {
    setUser({ ...user, [event.target.name]: event.target.value });
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    axios.patch(`/api/users/${user.id}/`, {
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
    })
      .then(response => {
        setUser(response.data);
        setSuccess("Profile updated successfully!");
      })
      .catch(() => {
        setError("Failed to update profile.");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  if (loading) return <CircularProgress />;
  if (error && !user) return <Alert severity="error">{error}</Alert>;
  if (!user) return <Alert severity="info">User not found.</Alert>;

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
      <Paper elevation={6} sx={{ padding: 4, width: '100%', maxWidth: 600 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Edit Profile
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Update your personal information.
        </Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            margin="normal"
            fullWidth
            id="username"
            label="Username"
            name="username"
            value={user.username}
            disabled
          />
          <TextField
            margin="normal"
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            value={user.email}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            fullWidth
            id="first_name"
            label="First Name"
            name="first_name"
            value={user.first_name}
            onChange={handleChange}
          />
          <TextField
            margin="normal"
            fullWidth
            id="last_name"
            label="Last Name"
            name="last_name"
            value={user.last_name}
            onChange={handleChange}
          />
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Save Changes'}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
}

export default ProfilePage;
