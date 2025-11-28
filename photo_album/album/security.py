"""
Security utilities for the photo album application.
"""
import os
import tempfile
from django.core.exceptions import ValidationError
from django.conf import settings
from PIL import Image

# Allowed file types
ALLOWED_IMAGE_TYPES = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
]

ALLOWED_VIDEO_TYPES = [
    'video/mp4',
    'video/avi',
    'video/mov',
    'video/wmv',
    'video/flv',
    'video/quicktime',
    'application/octet-stream',
]


def validate_file_type(uploaded_file, allowed_types):
    """
    Validate file type using both content-type and magic numbers.
    """
    # Check content-type first
    if uploaded_file.content_type not in allowed_types:
        # Fallback for octet-stream, check extension
        if uploaded_file.content_type == 'application/octet-stream':
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            allowed_extensions_map = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                '.gif': 'image/gif', '.webp': 'image/webp', '.mp4': 'video/mp4',
                '.avi': 'video/avi', '.mov': 'video/mov', '.wmv': 'video/wmv',
                '.flv': 'video/flv'
            }
            if file_extension in allowed_extensions_map and allowed_extensions_map[file_extension] in allowed_types:
                # If extension is allowed, trust it for octet-stream
                pass
            else:
                raise ValidationError(f"File type {uploaded_file.content_type} is not allowed.")
        else:
            raise ValidationError(f"File type {uploaded_file.content_type} is not allowed.")

    # Use python-magic for additional validation if available
    try:
        import magic
        file_magic = magic.Magic(mime=True)
        actual_mime = file_magic.from_buffer(uploaded_file.read(2048))
        uploaded_file.seek(0)  # Reset file pointer

        if actual_mime not in allowed_types:
            # Be lenient if magic detects octet-stream but content-type was valid
            if actual_mime != 'application/octet-stream':
                raise ValidationError(f"File content does not match allowed types. Detected: {actual_mime}")
    except ImportError:
        # python-magic not available, skip this check
        pass


from moviepy.editor import VideoFileClip
from .logging_utils import log_security_event

def validate_video_file(uploaded_file):
    """
    Additional validation for video files.
    """
    try:
        uploaded_file.seek(0)
        if hasattr(uploaded_file, 'temporary_file_path'):
            # For large files, Django saves them to a temporary file
            video_path = uploaded_file.temporary_file_path()
            VideoFileClip(video_path)
        else:
            # For small files, they are in memory. Write to a temp file to validate.
            with tempfile.NamedTemporaryFile(delete=True, suffix='.mov') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file.flush()
                VideoFileClip(temp_file.name)
        uploaded_file.seek(0)
    except Exception as e:
        raise ValidationError(f"Invalid video file: {str(e)}")


def validate_image_file(uploaded_file):
    """
    Additional validation for image files.
    """
    try:
        # Try to open the image to ensure it's valid
        img = Image.open(uploaded_file)
        img.verify()  # Verify the image is not corrupted
        uploaded_file.seek(0)  # Reset file pointer

        # Check image dimensions (prevent extremely large images)
        if hasattr(img, 'size'):
            width, height = img.size
            max_dimension = 10000  # Maximum allowed dimension
            if width > max_dimension or height > max_dimension:
                raise ValidationError(f"Image dimensions too large: {width}x{height}")

    except Exception as e:
        raise ValidationError(f"Invalid image file: {str(e)}")


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal and other security issues.
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove potentially dangerous characters
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')

    # Ensure filename is not empty and has an extension
    if not filename or '.' not in filename:
        filename = f"upload_{filename}" if filename else "upload"

    return filename


def check_file_size(uploaded_file, max_size=None):
    """
    Check file size against limits.
    """
    if max_size is None:
        max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE

    if uploaded_file.size > max_size:
        raise ValidationError(f"File size {uploaded_file.size} bytes exceeds maximum allowed size {max_size} bytes.")


from .logging_utils import log_security_event


def secure_file_upload(uploaded_file, allowed_types, is_image=False, user=None):
    """
    Complete file upload validation pipeline.
    """
    try:
        # Sanitize filename
        uploaded_file.name = sanitize_filename(uploaded_file.name)

        # Check file size with appropriate limits
        if is_image:
            max_size = 50 * 1024 * 1024  # 50MB for images
        else:
            max_size = 500 * 1024 * 1024  # 500MB for videos
        check_file_size(uploaded_file, max_size=max_size)

        # Validate file type
        validate_file_type(uploaded_file, allowed_types)

        # Additional image validation if it's an image
        if is_image:
            validate_image_file(uploaded_file)
        else:
            validate_video_file(uploaded_file)

        return uploaded_file
    except ValidationError as e:
        log_security_event(
            'file_upload_failed',
            user,
            f'File: {uploaded_file.name}, Error: {str(e)}'
        )
        raise e
