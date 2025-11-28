import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import { Grid, Card, CardActionArea, CardMedia, CardContent, Typography, CircularProgress, Alert, Button, Box } from '@mui/material';

function AlbumList() {
  const [albums, setAlbums] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get('/api/albums/')
      .then(response => {
        setAlbums(response.data.results);
        setLoading(false);
      })
      .catch(error => {
        console.error("There was an error fetching the albums!", error);
        setError("Failed to load albums. Please try again later.");
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
    <div>
      <Box sx={{ mb: 2 }}>
        <Button variant="contained" href="/upload/">
          Upload Photos
        </Button>
      </Box>
      <Grid container spacing={4}>
        {albums.map(album => (
          <Grid item xs={12} sm={6} md={4} key={album.id}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardActionArea component="a" href={`/albums/${album.id}/`}>
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
                  <Typography>
                    {album.description}
                  </Typography>
                </CardContent>
              </CardActionArea>
            </Card>
          </Grid>
        ))}
      </Grid>
    </div>
  );
}

export default AlbumList;
