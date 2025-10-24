import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import AlbumList from './components/AlbumList';
import AlbumDetail from './components/AlbumDetail';
import Homepage from './components/Homepage';
import LoginPage from './components/LoginPage';
import ProfilePage from './components/ProfilePage';
import RegistrationPage from './components/RegistrationPage';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
    background: {
      default: '#121212',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    }
  },
  components: {
    MuiListItem: {
      styleOverrides: {
        root: {
          color: '#b0bec5', // --text-secondary
          '&:hover': {
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            color: '#ffffff', // --text-primary
            '& .MuiListItemIcon-root': {
              color: '#ffffff',
            },
          },
        },
      },
    },
    MuiListItemIcon: {
      styleOverrides: {
        root: {
          color: '#b0bec5', // --text-secondary
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/dashboard" element={<AlbumList />} />
            <Route path="/album/albums/:id" element={<AlbumDetail />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/" element={<Homepage />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
