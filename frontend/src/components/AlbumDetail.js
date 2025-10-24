import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../api/axios';
import { Grid, Card, CardActionArea, CardMedia, CardContent, Typography, CircularProgress, Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, IconButton } from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import EditMediaModal from './EditMediaModal'; // Import the new modal

function AlbumDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [album, setAlbum] = useState(null);
  const [media, setMedia] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for modals
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [selectedMedia, setSelectedMedia] = useState(null);

  // ... (infinite scroll logic remains the same)
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const observer = useRef();

  const loadMoreMedia = useCallback(async () => {
    if (loading || !hasMore) return;
    setLoading(true);

    try {
      const response = await axios.get(`/api/albums/${id}/media/?page=${page}`);
      const newMedia = response.data.results;
      
      setMedia(prevMedia => {
        const existingIds = new Set(prevMedia.map(m => `${m.id}-${m.image ? 'photo' : 'video'}`));
        const uniqueNewMedia = newMedia.filter(m => !existingIds.has(`${m.id}-${m.image ? 'photo' : 'video'}`));
        return [...prevMedia, ...uniqueNewMedia];
      });
      
      if (response.data.next) {
        setPage(prev => prev + 1);
      } else {
        setHasMore(false);
      }
    } catch (err) {
      setError("Failed to load media.");
    } finally {
      setLoading(false);
    }
  }, [id, page, hasMore, loading]);

  const lastMediaElementRef = useCallback(node => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        loadMoreMedia();
      }
    });
    if (node) observer.current.observe(node);
  }, [loading, hasMore, loadMoreMedia]);

  useEffect(() => {
    const fetchInitialData = async () => {
      setLoading(true);
      try {
        const albumRes = await axios.get(`/api/albums/${id}/`);
        setAlbum(albumRes.data);
        loadMoreMedia(); // <--- ADD THIS LINE
      } catch (err) {
        setError("Failed to load album details.");
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, [id, loadMoreMedia]);

  const handleDeleteAlbum = () => {
    axios.delete(`/api/albums/${id}/`).then(() => navigate('/dashboard')).catch(() => setError("Failed to delete album."));
    setOpenDeleteDialog(false);
  };

  const handleDeleteMedia = () => {
    if (!selectedMedia) return;
    const url = selectedMedia.image ? `/api/photos/${selectedMedia.id}/` : `/api/videos/${selectedMedia.id}/`;
    axios.delete(url).then(() => {
      setMedia(media.filter(item => !(item.id === selectedMedia.id && (item.image ? 'photo' : 'video') === (selectedMedia.image ? 'photo' : 'video'))));
      setOpenDeleteDialog(false);
      setSelectedMedia(null);
    }).catch(() => setError("Failed to delete media."));
  };

  const handleMediaUpdated = (updatedMedia) => {
    setMedia(media.map(item => (item.id === updatedMedia.id && (item.image ? 'photo' : 'video') === (updatedMedia.image ? 'photo' : 'video')) ? updatedMedia : item));
  };

  const handleOpenEditModal = (mediaItem) => {
    setSelectedMedia(mediaItem);
    setOpenEditModal(true);
  };

  const handleOpenDeleteDialog = (mediaItem) => {
    setSelectedMedia(mediaItem);
    setOpenDeleteDialog(true);
  };

  if (!album && loading) return <CircularProgress />;
  if (error && !album) return <Alert severity="error">{error}</Alert>;
  if (!album) return <Alert severity="info">Album not found.</Alert>;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <div>
          <Typography variant="h3" gutterBottom>{album.title}</Typography>
          <Typography variant="body1" color="text.secondary" paragraph>{album.description}</Typography>
        </div>
        {album.is_owner && (
          <Box>
            <Button variant="outlined" startIcon={<EditIcon />} sx={{ mr: 1 }} href={`/album/edit/${id}`}>
              Edit Album
            </Button>
            <Button variant="contained" color="error" startIcon={<DeleteIcon />} onClick={() => handleOpenDeleteDialog(null)}>
              Delete Album
            </Button>
          </Box>
        )}
      </Box>
      
      <Grid container spacing={2}>
        {media.map((item, index) => {
          const isLastElement = media.length === index + 1;
          return (
            <Grid item xs={12} sm={6} md={4} lg={3} key={`${item.image ? 'photo' : 'video'}-${item.id}`} ref={isLastElement ? lastMediaElementRef : null}>
              <Card>
                <CardActionArea>
                  <CardMedia
                    component={item.image ? 'img' : 'video'}
                    height="200"
                    image={item.image && item.thumbnail ? item.thumbnail.url : item.video}
                    alt={item.title}
                    controls={!item.image}
                  />
                </CardActionArea>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography gutterBottom variant="h6" component="div" sx={{ flexGrow: 1, pr: 1 }}>
                      {item.title}
                    </Typography>
                    {item.is_owner && (
                      <Box>
                        <IconButton size="small" onClick={() => handleOpenEditModal(item)}>
                          <EditIcon />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleOpenDeleteDialog(item)}>
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>
      
      {loading && <CircularProgress sx={{ display: 'block', margin: '20px auto' }} />}
      {!hasMore && media.length > 0 && <Typography sx={{ textAlign: 'center', margin: '20px 0' }}>No more media to load.</Typography>}
      {media.length === 0 && !loading && <Alert severity="info">This album is empty.</Alert>}

      <Dialog open={openDeleteDialog} onClose={() => setOpenDeleteDialog(false)}>
        <DialogTitle>Delete {selectedMedia ? 'Media' : 'Album'}?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to permanently delete this {selectedMedia ? 'item' : 'album'}? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDeleteDialog(false)}>Cancel</Button>
          <Button onClick={selectedMedia ? handleDeleteMedia : handleDeleteAlbum} color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {selectedMedia && (
        <EditMediaModal
          open={openEditModal}
          handleClose={() => setOpenEditModal(false)}
          mediaItem={selectedMedia}
          onMediaUpdated={handleMediaUpdated}
        />
      )}
    </Box>
  );
}

export default AlbumDetail;