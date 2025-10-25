# This file contains all the @extend_schema decorators to be added to views.py
# Copy these decorators to the appropriate locations in album/api/views.py

# For RegistrationView.post (before def post):
"""
    @extend_schema(
        operation_id='user_registration',
        summary='Register a new user',
        description='Create a new user account with username, email, and password.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john_doe'},
                    'email': {'type': 'string', 'format': 'email', 'example': 'john@example.com'},
                    'password': {'type': 'string', 'format': 'password', 'example': 'SecurePass123!'}
                },
                'required': ['username', 'email', 'password']
            }
        },
        responses={201: UserSerializer, 400: OpenApiTypes.OBJECT},
        tags=['Authentication']
    )
"""

# For LoginView.post (before def post):
"""
    @extend_schema(
        operation_id='user_login',
        summary='Login a user',
        description='Authenticate with username and password.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'john_doe'},
                    'password': {'type': 'string', 'format': 'password', 'example': 'SecurePass123!'}
                },
                'required': ['username', 'password']
            }
        },
        responses={200: {'type': 'object', 'properties': {'user': UserSerializer}}, 400: OpenApiTypes.OBJECT},
        tags=['Authentication']
    )
"""

# For CurrentUserView.get (before def get):
"""
    @extend_schema(
        operation_id='get_current_user',
        summary='Get current user',
        description='Get currently authenticated user profile.',
        responses={200: UserSerializer, 401: OpenApiTypes.OBJECT},
        tags=['Authentication']
    )
"""

# For MediaUploadView.post (before def post):
"""
    @extend_schema(
        operation_id='media_upload',
        summary='Upload photo or video',
        description='Upload media file to an album.',
        request={'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {'type': 'string', 'format': 'binary'},
                'album_id': {'type': 'integer', 'example': 1}
            },
            'required': ['file', 'album_id']
        }},
        responses={201: PhotoSerializer, 400: OpenApiTypes.OBJECT, 403: OpenApiTypes.OBJECT, 404: OpenApiTypes.OBJECT},
        tags=['Media']
    )
"""
