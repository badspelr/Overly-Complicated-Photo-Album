"""
Base views and utilities for the album app.
"""
import logging
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.db import models
from django.contrib import messages
from ..models import Photo, Video, Album

logger = logging.getLogger(__name__)


def check_object_permission(user, obj, obj_type='album', action='view'):
    """Check if user has permission to access/modify an object."""
    if user.is_superuser:
        return True
    
    if obj_type == 'album':
        if action == 'delete':
            # Only album owner can delete albums
            return obj.owner == user
        else:
            # Check if user is owner, viewer, or album is public
            return obj.owner == user or obj.viewers.filter(pk=user.pk).exists() or obj.is_public
    elif obj_type in ['photo', 'video']:
        if action == 'delete':
            # Album owner can delete photos/videos, superusers can delete any
            return obj.album and (obj.album.owner == user or user.is_superuser)
        else:
            # Check if user can view the album containing the media
            return obj.album and (user.is_superuser or obj.album.owner == user or obj.album.viewers.filter(pk=user.pk).exists() or obj.album.is_public)
    elif obj_type == 'category':
        return obj.created_by == user
    
    return False


def get_delete_context(obj, obj_type, warning_message):
    """Generate context for delete confirmation templates."""
    return {
        'object_type': obj_type,
        'object_name': getattr(obj, 'title', getattr(obj, 'name', str(obj))),
        'warning_message': warning_message,
    }


class AlbumListPermissionMixin:
    """Mixin to handle album permissions for list views."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        model = self.model
        
        if user.is_superuser:
            return queryset
        
        if model == Album:
            return queryset.filter(
                models.Q(owner=user) | 
                models.Q(viewers=user) | 
                models.Q(is_public=True)
            )
        elif model in [Photo, Video]:
            return queryset.filter(
                models.Q(album__owner=user) |
                models.Q(album__viewers=user) |
                models.Q(album__is_public=True)
            )
        
        return queryset


class AlbumDetailPermissionMixin:
    """Mixin to handle album permissions for detail views."""

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return queryset

        q_filter = models.Q(is_public=True)
        if user.is_authenticated:
            q_filter |= models.Q(owner=user) | models.Q(viewers=user)

        model_name = self.model._meta.model_name
        if model_name == 'album':
            return queryset.filter(q_filter)
        elif model_name in ['photo', 'video']:
            album_q_filter = models.Q(album__is_public=True)
            if user.is_authenticated:
                album_q_filter |= models.Q(album__owner=user) | models.Q(album__viewers=user)
            return queryset.filter(album_q_filter)
        
        return queryset.none()
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not check_object_permission(self.request.user, obj, self.model._meta.model_name):
            log_security_event(f'unauthorized_access_{self.model._meta.model_name}', self.request.user, f'Object ID: {obj.pk}')
            raise PermissionDenied
        return obj


class AdminPermissionMixin:
    """Mixin to handle admin permissions."""

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name='Album Admin').exists()):
            messages.error(request, 'You do not have permission to perform this action.')
            log_security_event('unauthorized_admin_access', request.user)
            return redirect('album:dashboard')
        return super().dispatch(request, *args, **kwargs)


class CategoryPermissionMixin:
    """Mixin to handle category permissions."""

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return queryset
        return queryset.filter(created_by=user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not check_object_permission(self.request.user, obj, 'category'):
            log_security_event('unauthorized_access_category', self.request.user, f'Category ID: {obj.pk}')
            raise Http404
        return obj


def log_security_event(event_type, user, details=None):
    """Log security-related events."""
    logger.warning(f"Security Event: {event_type} - User: {user} - Details: {details}")


def log_user_action(action, user, object_type=None, object_id=None):
    """Log user actions for audit trail."""
    logger.info(f"User Action: {action} - User: {user} - Object: {object_type}:{object_id}")


def about_view(request):
    """Display the about page."""
    from django.shortcuts import render
    return render(request, 'album/about.html')


def contact_view(request):
    """Handle contact form submissions."""
    from django.shortcuts import render
    from django.core.mail import send_mail
    from django.conf import settings
    from ..forms import ContactForm
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Prepare email
            full_message = f"From: {name} <{email}>\n\n{message}"
            
            try:
                # Send email to site admins
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL] if hasattr(settings, 'CONTACT_EMAIL') else [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
                log_user_action('contact_form_submitted', request.user if request.user.is_authenticated else None, 'contact', email)
                return redirect('album:contact')
            except Exception as e:
                logger.error(f"Error sending contact email: {e}")
                messages.error(request, 'There was an error sending your message. Please try again later.')
    else:
        # Pre-fill form with user data if authenticated
        initial = {}
        if request.user.is_authenticated:
            initial['name'] = request.user.get_full_name() or request.user.username
            initial['email'] = request.user.email
        form = ContactForm(initial=initial)
    
    return render(request, 'album/contact.html', {'form': form})


def ai_settings_view(request):
    """Manage AI processing settings (admin only)."""
    from django.shortcuts import render
    from ..models import AIProcessingSettings
    from ..forms import AIProcessingSettingsForm
    
    # Only site admins can access AI settings
    if not request.user.is_site_admin:
        messages.error(request, 'You do not have permission to access AI settings.')
        return redirect('album:homepage')
    
    # Get or create the singleton settings instance
    settings_instance = AIProcessingSettings.load()
    
    if request.method == 'POST':
        form = AIProcessingSettingsForm(request.POST, instance=settings_instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'AI processing settings updated successfully.')
            log_user_action('ai_settings_updated', request.user, 'settings', settings_instance.id)
            return redirect('album:ai_settings')
    else:
        form = AIProcessingSettingsForm(instance=settings_instance)
    
    context = {
        'form': form,
        'settings': settings_instance,
    }
    
    return render(request, 'album/ai_settings.html', context)


def cookie_policy_view(request):
    """Display cookie policy page."""
    from django.shortcuts import render
    return render(request, 'album/cookie_policy.html')


def documentation_index(request):
    """Display documentation index page with links to all available documentation."""
    from django.shortcuts import render
    from pathlib import Path
    import os
    
    # Get the docs directory
    docs_dir = Path(__file__).resolve().parent.parent.parent / 'docs'
    
    # Organize documentation by category
    doc_categories = {
        'Getting Started': [],
        'User Guides': [],
        'Admin Guides': [],
        'Features': [],
        'Technical': [],
        'Development': [],
        'Deployment': [],
        'API': [],
    }
    
    # Scan docs directory if it exists
    if docs_dir.exists():
        for category_name, folder_name in [
            ('Getting Started', 'getting-started'),
            ('User Guides', 'user-guides'),
            ('Admin Guides', 'admin-guides'),
            ('Features', 'features'),
            ('Technical', 'technical'),
            ('Development', 'development'),
            ('Deployment', 'deployment'),
            ('API', 'api'),
        ]:
            category_dir = docs_dir / folder_name
            if category_dir.exists() and category_dir.is_dir():
                for md_file in sorted(category_dir.glob('*.md')):
                    # Skip README files in the list (they'll be linked as category intros)
                    if md_file.name != 'README.md':
                        doc_categories[category_name].append({
                            'title': md_file.stem.replace('_', ' ').replace('-', ' ').title(),
                            'filename': md_file.name,
                            'path': f'{folder_name}/{md_file.name}',
                        })
    
    context = {
        'doc_categories': doc_categories,
        'docs_available': any(docs for docs in doc_categories.values()),
    }
    
    return render(request, 'admin/documentation_index.html', context)


def documentation_view(request, doc_path):
    """Render a documentation markdown file with syntax highlighting."""
    from django.shortcuts import render
    from django.http import Http404
    from pathlib import Path
    import markdown
    from markdown.extensions.codehilite import CodeHiliteExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.toc import TocExtension
    
    # Security: Prevent directory traversal
    if '..' in doc_path or doc_path.startswith('/'):
        raise Http404("Invalid document path")
    
    # Get the docs directory
    docs_dir = Path(__file__).resolve().parent.parent.parent / 'docs'
    doc_file = docs_dir / doc_path
    
    # Security: Ensure the file is within docs directory
    try:
        doc_file = doc_file.resolve()
        docs_dir = docs_dir.resolve()
        if not str(doc_file).startswith(str(docs_dir)):
            raise Http404("Invalid document path")
    except (OSError, RuntimeError):
        raise Http404("Document not found")
    
    # Check if file exists and is a markdown file
    if not doc_file.exists() or not doc_file.is_file() or not doc_file.suffix == '.md':
        raise Http404("Document not found")
    
    # Read and render the markdown
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML with extensions
        md = markdown.Markdown(extensions=[
            FencedCodeExtension(),
            CodeHiliteExtension(css_class='highlight', linenums=False),
            TableExtension(),
            TocExtension(title='Table of Contents'),
            'nl2br',
            'sane_lists',
        ])
        html_content = md.convert(markdown_content)
        
        # Extract title from first h1 or use filename
        title = doc_file.stem.replace('_', ' ').replace('-', ' ').title()
        if '<h1>' in html_content:
            import re
            match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content)
            if match:
                title = match.group(1)
        
        context = {
            'title': title,
            'content': html_content,
            'doc_path': doc_path,
            'toc': md.toc if hasattr(md, 'toc') else '',
        }
        
        return render(request, 'admin/documentation_view.html', context)
        
    except Exception as e:
        logger.error(f"Error rendering documentation {doc_path}: {e}")
        raise Http404("Error rendering document")
