# Frontend Development Guide - Quick Reference

**Last Updated**: October 25, 2025  
**Strategy**: Hybrid (Django Templates + React Islands)

## Quick Decision Tree

```
Need to add a new feature?
│
├─ Is it highly interactive? (drag-drop, real-time, complex state)
│  └─ YES → Use React Component
│
├─ Is it simple CRUD or static content?
│  └─ YES → Use Django Template
│
├─ Does it need good SEO?
│  └─ YES → Start with Django Template, enhance with React if needed
│
└─ Not sure?
   └─ Default to Django Template, add React later if needed
```

---

## When to Use What

### Use Django Templates For:
✅ Authentication pages (login, register, password reset)  
✅ Admin interfaces  
✅ Simple forms (create album, edit profile)  
✅ Static content (about, terms, privacy policy)  
✅ Email templates  
✅ SEO-critical pages (album landing pages)  
✅ Base layout and navigation  

### Use React Components For:
⚡ Photo/video galleries with infinite scroll  
⚡ Drag-and-drop upload interfaces  
⚡ Real-time search with instant results  
⚡ Interactive image editing tools  
⚡ Bulk selection and operations  
⚡ Live notifications and progress indicators  
⚡ Complex UI with heavy client-side state  
⚡ Charts and data visualizations  

---

## File Structure

```
photo_album/
├── album/
│   ├── templates/album/        # Django templates
│   │   ├── base.html           # Base layout
│   │   ├── album_list.html     # Server-rendered album list
│   │   ├── album_detail.html   # Page with React gallery island
│   │   └── ...
│   └── views.py                # Django views
│
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── PhotoGallery.js # Embeddable in Django templates
│   │   │   ├── UploadWidget.js
│   │   │   └── SearchBox.js
│   │   ├── App.js              # Main React app (full SPA routes)
│   │   └── index.js
│   ├── public/
│   └── package.json
│
└── docs/technical/
    └── FRONTEND_STRATEGY.md    # This strategy document
```

---

## Creating a React Component Island

### Step 1: Create React Component
```jsx
// frontend/src/components/PhotoGallery.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function PhotoGallery({ albumId }) {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`/api/albums/${albumId}/media/`)
      .then(response => {
        setPhotos(response.data.results);
        setLoading(false);
      })
      .catch(error => console.error('Error:', error));
  }, [albumId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="photo-gallery">
      {photos.map(photo => (
        <img 
          key={photo.id} 
          src={photo.thumbnail} 
          alt={photo.title}
        />
      ))}
    </div>
  );
}
```

### Step 2: Create Entry Point
```jsx
// frontend/src/photoGalleryEntry.js
import React from 'react';
import ReactDOM from 'react-dom';
import PhotoGallery from './components/PhotoGallery';

// Find all photo gallery containers and render
document.querySelectorAll('[data-photo-gallery]').forEach(container => {
  const albumId = container.dataset.albumId;
  ReactDOM.render(
    <PhotoGallery albumId={albumId} />,
    container
  );
});
```

### Step 3: Update webpack Config
```javascript
// frontend/craco.config.js
module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig.entry = {
        main: './src/index.js',
        photoGallery: './src/photoGalleryEntry.js',
      };
      return webpackConfig;
    },
  },
};
```

### Step 4: Embed in Django Template
```django
{# album/templates/album/album_detail.html #}
{% extends 'album/base.html' %}
{% load render_bundle from webpack_loader %}

{% block content %}
<h1>{{ album.title }}</h1>

<!-- React component will mount here -->
<div 
  data-photo-gallery 
  data-album-id="{{ album.id }}"
  id="photo-gallery-root">
  <!-- Fallback content (no JS) -->
  {% for photo in photos %}
    <img src="{{ photo.image.url }}" alt="{{ photo.title }}">
  {% endfor %}
</div>

<!-- Load React component -->
{% render_bundle 'photoGallery' 'js' %}
{% endblock %}
```

---

## API Communication

### CSRF Token in React
```javascript
// Get CSRF token from cookie
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

// Configure axios
import axios from 'axios';

axios.defaults.xsrfHeaderName = 'X-CSRFToken';
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.withCredentials = true;

// Use in components
axios.post('/api/albums/', data)
  .then(response => console.log('Success!'))
  .catch(error => console.error('Error:', error));
```

### Authentication Check
```javascript
// Check if user is authenticated
axios.get('/api/current-user/')
  .then(response => {
    if (response.data) {
      // User is logged in
      setUser(response.data);
    } else {
      // Redirect to login
      window.location.href = '/login/';
    }
  });
```

---

## Styling Guidelines

### Use Material-UI for React Components
```jsx
import { Button, Card, Grid } from '@mui/material';

function MyComponent() {
  return (
    <Card>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Button variant="contained" color="primary">
            Upload Photos
          </Button>
        </Grid>
      </Grid>
    </Card>
  );
}
```

### Match Django Theme
```javascript
// frontend/src/theme.js
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',  // Match Django dark theme
    primary: {
      main: '#90caf9',  // Match Django primary color
    },
    secondary: {
      main: '#f48fb1',  // Match Django secondary color
    },
  },
});
```

---

## Testing

### React Component Tests
```javascript
// frontend/src/components/PhotoGallery.test.js
import { render, screen, waitFor } from '@testing-library/react';
import PhotoGallery from './PhotoGallery';
import axios from 'axios';

jest.mock('axios');

test('renders photo gallery', async () => {
  axios.get.mockResolvedValue({
    data: {
      results: [
        { id: 1, thumbnail: '/media/photo1.jpg', title: 'Photo 1' },
      ],
    },
  });

  render(<PhotoGallery albumId={1} />);
  
  await waitFor(() => {
    expect(screen.getByAlt('Photo 1')).toBeInTheDocument();
  });
});
```

### Django Integration Tests
```python
# album/tests/test_views.py
from django.test import TestCase

class AlbumDetailViewTest(TestCase):
    def test_album_detail_with_react_component(self):
        response = self.client.get(f'/albums/{self.album.id}/')
        self.assertContains(response, 'data-photo-gallery')
        self.assertContains(response, 'photo-gallery-root')
```

---

## Development Workflow

### Running Development Servers

**Terminal 1: Django**
```bash
docker compose up
# Django runs on http://localhost:8000
```

**Terminal 2: React (optional, for hot reload)**
```bash
cd frontend
npm start
# React dev server runs on http://localhost:3000
```

### Building for Production
```bash
# Build React bundles
cd frontend
npm run build

# Collect static files
docker compose exec web python manage.py collectstatic --noinput

# Restart Django
docker compose restart web
```

---

## Common Patterns

### Pattern 1: Progressive Enhancement
```django
<!-- Works without JavaScript -->
<form method="post" action="{% url 'upload_photo' %}" enctype="multipart/form-data">
  {% csrf_token %}
  <input type="file" name="photo" accept="image/*">
  <button type="submit">Upload</button>
</form>

<!-- Enhanced with React -->
<div id="react-upload-widget"></div>
<script>
  if (window.ReactDOM) {
    // Mount React component
    ReactDOM.render(<UploadWidget />, document.getElementById('react-upload-widget'));
    // Hide fallback form
    document.querySelector('form').style.display = 'none';
  }
</script>
```

### Pattern 2: Server-Rendered Data
```django
<!-- Pass initial data from Django -->
<div 
  id="photo-gallery" 
  data-photos='{{ photos_json|safe }}'
  data-album-id="{{ album.id }}">
</div>

<script>
  const container = document.getElementById('photo-gallery');
  const initialPhotos = JSON.parse(container.dataset.photos);
  ReactDOM.render(
    <PhotoGallery initialPhotos={initialPhotos} albumId={container.dataset.albumId} />,
    container
  );
</script>
```

### Pattern 3: API-Driven Updates
```jsx
// Optimistic update + API sync
function deletePhoto(photoId) {
  // 1. Update UI immediately
  setPhotos(photos => photos.filter(p => p.id !== photoId));
  
  // 2. Sync with server
  axios.delete(`/api/photos/${photoId}/`)
    .then(() => {
      // Success! UI already updated
      showNotification('Photo deleted');
    })
    .catch(error => {
      // Rollback UI change
      setPhotos(originalPhotos);
      showError('Failed to delete photo');
    });
}
```

---

## Deployment Checklist

### Before Deploying React Changes

- [ ] Run tests: `npm test`
- [ ] Build production bundle: `npm run build`
- [ ] Check bundle size: `ls -lh frontend/build/static/js/`
- [ ] Test without React (progressive enhancement)
- [ ] Test with slow network (throttle in DevTools)
- [ ] Verify CSRF token handling
- [ ] Check console for errors
- [ ] Run Lighthouse audit

### After Deployment

- [ ] Verify static files collected
- [ ] Check browser console for errors
- [ ] Test user workflows
- [ ] Monitor Sentry for errors
- [ ] Check API response times
- [ ] Verify mobile responsiveness

---

## Troubleshooting

### React Component Not Mounting
1. Check webpack-stats.json exists
2. Verify bundle path in settings.py
3. Check browser console for errors
4. Ensure `render_bundle` loads correct file

### CSRF Token Errors
1. Verify csrftoken cookie is set
2. Check axios CSRF configuration
3. Ensure `withCredentials: true` in axios
4. Check Django CSRF_COOKIE_HTTPONLY setting

### Styles Not Applied
1. Check Material-UI theme provider wraps component
2. Verify CSS imports in entry file
3. Check for CSS specificity conflicts
4. Ensure collectstatic ran after build

### API Calls Failing
1. Check network tab in DevTools
2. Verify API endpoint exists (`/api/schema/`)
3. Check authentication status
4. Verify CORS settings if needed

---

## Performance Tips

### Code Splitting
```javascript
// Lazy load heavy components
const PhotoEditor = React.lazy(() => import('./components/PhotoEditor'));

function App() {
  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <PhotoEditor />
    </React.Suspense>
  );
}
```

### Optimize Images
```jsx
// Use thumbnail for list, full size on click
<img 
  src={photo.thumbnail} 
  loading="lazy"
  onClick={() => openFullSize(photo.image)}
/>
```

### Cache API Responses
```javascript
// Use React Query for automatic caching
import { useQuery } from 'react-query';

function usePhotos(albumId) {
  return useQuery(['photos', albumId], () =>
    axios.get(`/api/albums/${albumId}/media/`).then(r => r.data)
  );
}
```

---

## Resources

- [Django Webpack Loader Docs](https://github.com/django-webpack/django-webpack-loader)
- [Material-UI Documentation](https://mui.com/)
- [React Router](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)
- [React Query](https://tanstack.com/query/latest)

---

**Questions?** Check the main strategy document: `docs/technical/FRONTEND_STRATEGY.md`
