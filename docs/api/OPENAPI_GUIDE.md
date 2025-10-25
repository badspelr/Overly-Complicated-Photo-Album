# OpenAPI / Swagger API Documentation Guide

## Overview

Photo Album now includes comprehensive, interactive API documentation powered by **drf-spectacular**. This provides three interfaces for exploring and testing the API:

1. **Swagger UI** - Interactive API testing interface
2. **ReDoc** - Clean, user-friendly documentation viewer  
3. **Raw OpenAPI Schema** - Machine-readable API specification

## Accessing the Documentation

### Swagger UI (Recommended for Testing)
```
http://localhost:8000/api/docs/
```
- **Best for**: Interactive API testing and exploration
- **Features**: Try out API calls directly in the browser
- **Authentication**: Supports session and token authentication

### ReDoc
```
http://localhost:8000/api/redoc/
```
- **Best for**: Reading documentation and understanding API structure
- **Features**: Clean, responsive design with search functionality
- **View**: Three-column layout with navigation

### Raw OpenAPI Schema
```
http://localhost:8000/api/schema/
```
- **Format**: YAML (OpenAPI 3.0.3)
- **Best for**: Generating client SDKs, importing into API tools
- **Use cases**: Postman import, code generation, automated testing

## Using Swagger UI

### 1. Authentication

The API supports two authentication methods:

#### Session Authentication (Default)
1. Login through the Django admin: `http://localhost:8000/admin/`
2. Return to Swagger UI - you're automatically authenticated
3. Look for the green "Authorized" badge

#### Token Authentication
1. Click the **"Authorize"** button (top right, lock icon)
2. In the "tokenAuth" section, enter: `Token <your-token>`
3. Click **"Authorize"** then **"Close"**
4. You're now authenticated for all requests

### 2. Testing API Endpoints

#### Example: Register a New User
1. Find the **"Authentication"** section in Swagger UI
2. Click on **POST /api/register/**
3. Click **"Try it out"**
4. Edit the request body:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```
5. Click **"Execute"**
6. View the response below (should be 201 Created)

#### Example: Create an Album
1. Make sure you're authenticated
2. Find **POST /api/albums/**
3. Click **"Try it out"**
4. Enter album details:
```json
{
  "title": "My Vacation Photos",
  "description": "Summer 2025 trip to the mountains",
  "is_public": false
}
```
5. Click **"Execute"**
6. Note the album ID in the response

#### Example: Upload a Photo
1. Find **POST /api/media/upload/**
2. Click **"Try it out"**
3. Click **"Choose File"** and select an image
4. Enter the `album_id` from the previous step
5. Click **"Execute"**
6. The photo will be uploaded and metadata extracted

### 3. Filtering and Pagination

Many endpoints support filtering:

#### List Albums with Filters
```
GET /api/albums/?is_public=true&ordering=-created_at&page_size=10
```

In Swagger UI:
1. Click on **GET /api/albums/**
2. Click **"Try it out"**
3. Fill in the parameters:
   - `is_public`: true
   - `ordering`: -created_at
   - `page_size`: 10
4. Click **"Execute"**

## API Organization

The API is organized into the following sections:

### 🔐 Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - Login user
- `GET /api/current-user/` - Get current user profile

### 📁 Albums
- `GET /api/albums/` - List all accessible albums
- `POST /api/albums/` - Create new album
- `GET /api/albums/{id}/` - Get album details
- `PUT/PATCH /api/albums/{id}/` - Update album
- `DELETE /api/albums/{id}/` - Delete album
- `GET /api/albums/{id}/media/` - Get album media
- `POST /api/albums/{id}/toggle_viewer/` - Add/remove viewer

### 📷 Photos
- `GET /api/photos/` - List photos
- `POST /api/photos/` - Create photo
- `GET /api/photos/{id}/` - Get photo details
- `PUT/PATCH /api/photos/{id}/` - Update photo
- `DELETE /api/photos/{id}/` - Delete photo

### 🎥 Videos
- `GET /api/videos/` - List videos
- `POST /api/videos/` - Create video
- `GET /api/videos/{id}/` - Get video details
- `PUT/PATCH /api/videos/{id}/` - Update video
- `DELETE /api/videos/{id}/` - Delete video

### 📂 Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Get category
- `PUT/PATCH /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### 📤 Media
- `POST /api/media/upload/` - Upload photo/video
- `POST /api/bulk-edit/` - Bulk edit multiple items

### 👥 Users
- `GET /api/users/` - List users
- `GET /api/users/me/` - Get own profile
- `PUT/PATCH /api/users/{id}/` - Update user

### ⚙️ Settings
- `GET /api/site-settings/` - Get site settings
- `PUT/PATCH /api/site-settings/{id}/` - Update settings (admin only)

## Common Operations

### Searching
Use the `search` parameter on list endpoints:
```
GET /api/photos/?search=vacation
GET /api/albums/?search=summer
```

### Ordering
Use the `ordering` parameter:
```
GET /api/photos/?ordering=-uploaded_at  # Newest first
GET /api/albums/?ordering=title  # Alphabetical
```

### Pagination
Control pagination with `page` and `page_size`:
```
GET /api/photos/?page=2&page_size=50
```

## Response Codes

- **200 OK** - Successful GET/PUT/PATCH request
- **201 Created** - Successful POST request
- **204 No Content** - Successful DELETE request
- **400 Bad Request** - Invalid data submitted
- **401 Unauthorized** - Authentication required
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource doesn't exist

## Tips and Tricks

### 1. Persistent Authorization
Enable **"Persist authorization data"** in Swagger UI settings (top right gear icon). This saves your authentication between page reloads.

### 2. Deep Linking
Enable **"Deep linking"** to share direct links to specific API endpoints.

### 3. Request Filtering
Use the filter box at the top to quickly find endpoints:
- Type "photo" to find all photo-related endpoints
- Type "upload" to find upload endpoints

### 4. Exploring Response Schemas
Click on any endpoint's response to see the full data structure, including:
- Field types
- Required vs optional fields
- Example values
- Nested objects

### 5. Download OpenAPI Spec
You can download the raw OpenAPI specification for use in other tools:
```bash
curl http://localhost:8000/api/schema/ > openapi.yaml
```

## Generating Client SDKs

Use the OpenAPI schema to generate client libraries:

### Python Client
```bash
# Using openapi-generator
openapi-generator-cli generate \
  -i http://localhost:8000/api/schema/ \
  -g python \
  -o ./python-client
```

### JavaScript Client
```bash
openapi-generator-cli generate \
  -i http://localhost:8000/api/schema/ \
  -g javascript \
  -o ./js-client
```

## Troubleshooting

### Can't see any endpoints
- Make sure the Docker container is running: `docker-compose ps`
- Check for errors: `docker logs photo_album_web`

### Authentication not working
- Clear browser cookies and try again
- Try token authentication instead of session authentication
- Verify your user account is active

### Uploads fail in Swagger UI
- File uploads require multipart/form-data
- Ensure the album exists and you have permission
- Check the file size (may have server limits)

## Production Considerations

### Security
In production, you may want to:
1. Restrict documentation access to authenticated users
2. Update `SPECTACULAR_SETTINGS` → `SERVE_PERMISSIONS`
3. Consider disabling Swagger UI entirely
4. Keep ReDoc for documentation, disable the raw schema

### Performance
- The schema is generated dynamically
- Consider caching the schema in production
- Use CDN for Swagger UI static assets

## Additional Resources

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger UI Documentation](https://swagger.io/tools/swagger-ui/)
- [ReDoc Documentation](https://redocly.com/docs/redoc/)

## Support

For issues or questions:
1. Check the Django logs: `docker logs photo_album_web`
2. Review the OpenAPI schema for errors
3. Consult the drf-spectacular documentation
4. Open an issue in the project repository

---

**Last Updated**: October 2025  
**API Version**: 1.3.0  
**OpenAPI Version**: 3.0.3
