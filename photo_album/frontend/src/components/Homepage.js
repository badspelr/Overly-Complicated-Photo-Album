import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Grid, Card, CardActionArea, CardMedia, CardContent, Typography, CircularProgress, Alert, Box } from '@mui/material';

function Homepage() {
  const [publicAlbums, setPublicAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('/api/albums/?is_public=true')
      .then(response => {
        setPublicAlbums(response.data.results);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching public albums:", error);
        setError("Failed to load public albums.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box>
      <Typography variant="h3" gutterBottom>Public Gallery</Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Welcome! Here are the publicly shared albums from all our users.
      </Typography>
      <Grid container spacing={4}>
        {publicAlbums.map(album => (
          <Grid item xs={12} sm={6} md={4} key={album.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardActionArea component="a" href={`/album/albums/${album.id}/`}>
                <CardMedia
                  component="img"
                  height="140"
                  image={album.cover_photo || `https://via.placeholder.com/300x140.png?text=${album.title}`}
                  alt={album.title}
                />
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography gutterBottom variant="h5" component="h2">
                    {album.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    by {album.owner.username}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Homepage;
