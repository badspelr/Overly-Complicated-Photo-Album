import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import { AppBar, Toolbar, Typography, Drawer, List, ListItem, ListItemIcon, ListItemText, Box, Button, CircularProgress } from '@mui/material';
import PhotoAlbumIcon from '@mui/icons-material/PhotoAlbum';
import HomeIcon from '@mui/icons-material/Home';
import UploadIcon from '@mui/icons-material/Upload';
import AddIcon from '@mui/icons-material/Add';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import CategoryIcon from '@mui/icons-material/Category';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import CreateAlbumModal from './CreateAlbumModal';
import CreateCategoryModal from './CreateCategoryModal';
import InviteUserModal from './InviteUserModal';

const drawerWidth = 240;

// Helper to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function Layout({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loadingUser, setLoadingUser] = useState(true);
  
  const [albumModalOpen, setAlbumModalOpen] = useState(false);
  const [categoryModalOpen, setCategoryModalOpen] = useState(false);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);

  useEffect(() => {
    axios.get('/api/user/me/')
      .then(response => {
        setCurrentUser(response.data);
      })
      .catch(() => {
        setCurrentUser(null);
      })
      .finally(() => {
        setLoadingUser(false);
      });
  }, []);

  const handleAlbumModalOpen = () => setAlbumModalOpen(true);
  const handleAlbumModalClose = () => setAlbumModalOpen(false);
  const handleAlbumCreated = () => window.location.reload();
  const handleCategoryModalOpen = () => setCategoryModalOpen(true);
  const handleCategoryModalClose = () => setCategoryModalOpen(false);
  const handleCategoryCreated = () => window.location.reload();
  const handleInviteModalOpen = () => setInviteModalOpen(true);
  const handleInviteModalClose = () => setInviteModalOpen(false);
  const handleUserInvited = () => window.location.reload();

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <PhotoAlbumIcon sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
            Photo Album
          </Typography>
          
          {loadingUser ? (
            <CircularProgress color="inherit" size={24} />
          ) : currentUser ? (
            <>
              <Typography sx={{ mr: 2 }}>Welcome, {currentUser.username}</Typography>
              <form action="/accounts/logout/" method="post" style={{ display: 'inline' }}>
                <input type="hidden" name="csrfmiddlewaretoken" value={getCookie('csrftoken')} />
                <Button color="inherit" type="submit" sx={{ ml: 1 }}>Logout</Button>
              </form>
            </>
          ) : (
            <Button color="inherit" href="/accounts/login/">Login</Button>
          )}
        </Toolbar>
      </AppBar>
      
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: { width: drawerWidth, boxSizing: 'border-box' },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto' }}>
          <List>
            <ListItem button component="a" href="/dashboard/">
              <ListItemIcon>
                <HomeIcon />
              </ListItemIcon>
              <ListItemText primary="Dashboard" />
            </ListItem>
            <ListItem button component="a" href="/upload/">
              <ListItemIcon>
                <UploadIcon />
              </ListItemIcon>
              <ListItemText primary="Upload" />
            </ListItem>
            <ListItem button onClick={handleAlbumModalOpen} sx={{ cursor: 'pointer' }}>
              <ListItemIcon>
                <AddIcon />
              </ListItemIcon>
              <ListItemText primary="Create Album" />
            </ListItem>
            <ListItem button onClick={handleCategoryModalOpen} sx={{ cursor: 'pointer' }}>
              <ListItemIcon>
                <CategoryIcon />
              </ListItemIcon>
              <ListItemText primary="Create Category" />
            </ListItem>
            <ListItem button onClick={handleInviteModalOpen} sx={{ cursor: 'pointer' }}>
              <ListItemIcon>
                <PersonAddIcon />
              </ListItemIcon>
              <ListItemText primary="Invite User" />
            </ListItem>
            <ListItem button component="a" href="/profile/">
              <ListItemIcon>
                <AccountCircleIcon />
              </ListItemIcon>
              <ListItemText primary="Profile" />
            </ListItem>
          </List>
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {children}
      </Box>
      <CreateAlbumModal open={albumModalOpen} handleClose={handleAlbumModalClose} onAlbumCreated={handleAlbumCreated} />
      <CreateCategoryModal open={categoryModalOpen} handleClose={handleCategoryModalClose} onCategoryCreated={handleCategoryCreated} />
      <InviteUserModal open={inviteModalOpen} handleClose={handleInviteModalClose} onUserInvited={handleUserInvited} />
    </Box>
  );
}

export default Layout;