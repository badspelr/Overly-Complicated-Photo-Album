from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db import models
from .models import Photo, Video, Album, Category, Tag, CustomAlbum, AIProcessingSettings

# Custom widget to allow multiple file uploads correctly
class MultipleFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        # We have to call the grandparent's __init__ to bypass the 'multiple' check
        super(forms.FileInput, self).__init__(attrs)

class UserInvitationForm(forms.Form):
    email = forms.EmailField(
        help_text="Enter the email address of the person you want to invite",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'off'})
    )
    albums = forms.ModelMultipleChoiceField(
        queryset=Album.objects.none(),
        help_text="Select the albums to share (you can select multiple)",
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    username = forms.CharField(
        max_length=150,
        required=False,
        help_text="Enter a username if creating a new user",
        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        required=False,
        help_text="Enter a password if creating a new user"
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select user groups to assign this user to. If none selected, user will be assigned to Viewer group.",
        initial=['Viewer']  # Default to Viewer group
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        help_text="Check to make the user account active immediately",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if hasattr(user, 'is_site_admin') and user.is_site_admin:
                # Site admins can invite users to their own albums and create users
                self.fields['albums'].queryset = Album.objects.filter(owner=user)
            elif hasattr(user, 'is_album_admin') and user.is_album_admin:
                # Album admins can only invite to albums they own, no user creation
                self.fields['albums'].queryset = Album.objects.filter(owner=user)
                # Hide user creation fields
                self.fields['username'].widget = forms.HiddenInput()
                self.fields['password'].widget = forms.HiddenInput()
                self.fields['groups'].widget = forms.HiddenInput()
                self.fields['is_active'].widget = forms.HiddenInput()
                # Make them not required
                self.fields['username'].required = False
                self.fields['password'].required = False
            else:
                # Regular users can only invite to albums they own
                self.fields['albums'].queryset = Album.objects.filter(owner=user)

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'autocomplete': 'off'}))
    agree_to_terms = forms.BooleanField(
        required=True,
        label='I have read and agree to the Terms of Conduct and CSAM Policy',
        error_messages={'required': 'You must agree to the terms to create an account'},
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
            'first_name': forms.TextInput(attrs={'autocomplete': 'off'}),
            'last_name': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set autocomplete for password fields
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

class CustomUserChangeForm(UserChangeForm):
    """Form for regular users to edit their own profile - NO group management allowed."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from the form
        if 'password' in self.fields:
            del self.fields['password']


class AdminUserChangeForm(UserChangeForm):
    """Form for administrators to edit users with group management capabilities."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'style': 'margin-left:0.5em;'}),
        label="Active"
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select user groups to assign this user to."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field from the form
        if 'password' in self.fields:
            del self.fields['password']
        if self.instance and self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            if self.cleaned_data.get('groups'):
                user.groups.set(self.cleaned_data['groups'])
            else:
                user.groups.clear()
        return user


class AlbumAdminUserChangeForm(forms.ModelForm):
    """Form for Album Admins to edit user details, with restricted group management."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off', 'class': 'form-control', 'style': 'max-width:400px; display:inline-block;'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'style': 'margin-left:0.5em;'}),
        label="Active"
    )
    album_admin = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'style': 'margin-left:0.5em;'}),
        label="Album Admin",
        help_text="Grant or revoke Album Admin privileges."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password field
        if 'password' in self.fields:
            del self.fields['password']
        if self.instance and self.instance.pk:
            # Set initial value for album_admin checkbox
            self.fields['album_admin'].initial = self.instance.groups.filter(name='Album Admin').exists()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Handle Album Admin group
            album_admin_group, _ = Group.objects.get_or_create(name='Album Admin')
            if self.cleaned_data.get('album_admin'):
                user.groups.add(album_admin_group)
            else:
                user.groups.remove(album_admin_group)
        return user


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['title', 'description', 'category', 'cover_image', 'is_public']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if user.is_superuser:
                # Superusers can see all categories
                self.fields['category'].queryset = Category.objects.all()
            else:
                # Regular users can only see categories they created
                self.fields['category'].queryset = Category.objects.filter(created_by=user)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name...',
                'style': 'background-image: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\' class=\'material-icons\'%3E%3Cpath d=\'M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.83z\'/%3E%3Cline x1=\'7\' y1=\'7\' x2=\'7.01\' y2=\'7\'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: 10px center; padding-left: 40px;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter category description...',
                'style': 'background-image: url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'24\' height=\'24\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'currentColor\' stroke-width=\'2\' stroke-linecap=\'round\' stroke-linejoin=\'round\' class=\'material-icons\'%3E%3Cpath d=\'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z\'/%3E%3Cpolyline points=\'14,2 14,8 20,8\'/%3E%3Cline x1=\'16\' y1=\'13\' x2=\'8\' y2=\'13\'/%3E%3Cline x1=\'16\' y1=\'17\' x2=\'8\' y2=\'17\'/%3E%3Cpolyline points=\'10,9 9,9 8,9\'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: 10px 10px; padding-left: 40px; padding-top: 10px;'
            }),
        }


# Form for editing photo metadata (admin use)
class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = [
            'category', 'title', 'description',
            'date_taken', 'camera_make', 'camera_model', 'latitude', 'longitude'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'date_taken': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'camera_make': forms.TextInput(attrs={'class': 'form-control'}),
            'camera_model': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }


# --- Tag and Custom Album fields ---
class TagField(forms.CharField):
    """Custom field for comma-separated tags with autocomplete support."""
    def prepare_value(self, value):
        # Always display as a comma-separated string
        if isinstance(value, list):
            return ', '.join([str(v) for v in value])
        return value or ''

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, list):
            # Already a list (shouldn't happen for input, but just in case)
            return [str(t).strip() for t in value if str(t).strip()]
        return [t.strip() for t in value.split(',') if t.strip()]

class PhotoForm(forms.ModelForm):
    tags = TagField(required=False, help_text="Comma-separated tags. Start typing to see suggestions.")
    custom_albums = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'custom-album-select'})
    )

    class Meta:
        model = Photo
        fields = ['album', 'category', 'title', 'description', 'image', 'tags', 'custom_albums', 
                  'date_taken', 'camera_make', 'camera_model', 'latitude', 'longitude']
        widgets = {
            'date_taken': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'camera_make': forms.TextInput(attrs={'class': 'form-control'}),
            'camera_model': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from .models import CustomAlbum
            self.fields['custom_albums'].queryset = CustomAlbum.objects.filter(owner=user)
        else:
            from .models import CustomAlbum
            self.fields['custom_albums'].queryset = CustomAlbum.objects.none()
        if self.instance.pk:
            # When editing an existing photo, remove the image field (we don't want to replace the image)
            if 'image' in self.fields:
                del self.fields['image']
            tag_names = [t.name for t in self.instance.tags.all()]
            self.fields['tags'].initial = ', '.join(tag_names) if tag_names else ''
            self.fields['custom_albums'].initial = self.instance.custom_albums.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        tags = self.cleaned_data.get('tags', [])
        if commit:
            instance.save()
            # Handle tags
            from .models import Tag
            tag_objs = []
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name, defaults={'created_by': instance.album.owner})
                tag_objs.append(tag_obj)
            instance.tags.set(tag_objs)
            # Handle custom albums
            instance.custom_albums.set(self.cleaned_data.get('custom_albums', []))
        return instance

class VideoForm(forms.ModelForm):
    tags = TagField(required=False, help_text="Comma-separated tags. Start typing to see suggestions.")
    custom_albums = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'custom-album-select'})
    )

    class Meta:
        model = Video
        fields = ['album', 'category', 'title', 'description', 'video', 'tags', 'custom_albums', 'date_recorded']
        widgets = {
            'date_recorded': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            from .models import CustomAlbum
            self.fields['custom_albums'].queryset = CustomAlbum.objects.filter(owner=user)
        else:
            from .models import CustomAlbum
            self.fields['custom_albums'].queryset = CustomAlbum.objects.none()
        if self.instance.pk:
            # When editing an existing video, remove the video field (we don't want to replace the video)
            if 'video' in self.fields:
                del self.fields['video']
            tag_names = [t.name for t in self.instance.tags.all()]
            self.fields['tags'].initial = ', '.join(tag_names) if tag_names else ''
            self.fields['custom_albums'].initial = self.instance.custom_albums.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        tags = self.cleaned_data.get('tags', [])
        if commit:
            instance.save()
            # Handle tags
            from .models import Tag
            tag_objs = []
            for tag_name in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag_name, defaults={'created_by': instance.album.owner})
                tag_objs.append(tag_obj)
            instance.tags.set(tag_objs)
            # Handle custom albums
            instance.custom_albums.set(self.cleaned_data.get('custom_albums', []))
        return instance
# ...existing code...

# Tag and CustomAlbum management forms
class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

class CustomAlbumForm(forms.ModelForm):
    class Meta:
        model = CustomAlbum
        fields = ['title', 'description']

class MediaUploadForm(forms.Form):
    album = forms.ModelChoiceField(queryset=Album.objects.none(), required=False, empty_label="Select Album (optional)")
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False, empty_label="Select Category (optional)")
    title = forms.CharField(max_length=100, required=False, help_text="Optional title for uploaded files")
    description = forms.CharField(widget=forms.Textarea, required=False)
    media_files = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True}), required=False, help_text="Select individual files")
    media_dir = forms.FileField(widget=MultipleFileInput(attrs={'webkitdirectory': True, 'directory': True, 'multiple': True}), required=False, help_text="Or select a directory to upload")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Get albums the user can upload to
            user_albums = Album.objects.filter(
                models.Q(owner=self.user) | 
                models.Q(viewers=self.user) | 
                models.Q(is_public=True)
            ).distinct()
            
            # Check if user is an album admin (superuser or owns any albums)
            is_admin = self.user.is_superuser or Album.objects.filter(owner=self.user).exists()
            
            if is_admin:
                # Make album required for album admins
                self.fields['album'].required = True
                self.fields['album'].empty_label = "Select Album (required)"
                self.fields['album'].help_text = "You must select an album to upload files"
            else:
                # Keep album optional for regular users
                self.fields['album'].required = False
                self.fields['album'].empty_label = "Select Album (optional)"
                self.fields['album'].help_text = "Optional: Select an album to organize your uploads"
            
            self.fields['album'].queryset = user_albums
            
            # Set category queryset based on user's categories
            user_categories = Category.objects.filter(created_by=self.user)
            self.fields['category'].queryset = user_categories

class ViewerForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), label="Select User")


class ContactForm(forms.Form):
    """Form for users to send contact/feedback messages"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email Address'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message',
            'rows': 6
        })
    )


class AIProcessingSettingsForm(forms.ModelForm):
    """Form for managing AI processing settings"""
    class Meta:
        model = AIProcessingSettings
        fields = [
            'auto_process_on_upload',
            'scheduled_processing',
            'batch_size',
            'processing_timeout',
            'schedule_hour',
            'schedule_minute',
        ]
        widgets = {
            'auto_process_on_upload': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'scheduled_processing': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'batch_size': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '10000'
            }),
            'processing_timeout': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '300'
            }),
            'schedule_hour': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '23'
            }),
            'schedule_minute': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '59'
            }),
        }
        help_texts = {
            'auto_process_on_upload': 'Automatically process photos and videos with AI when they are uploaded',
            'scheduled_processing': 'Enable scheduled processing of unprocessed media at a specific time each day',
            'batch_size': 'Number of items to process in each batch (default: 500)',
            'processing_timeout': 'Timeout in seconds for each item (default: 30)',
            'schedule_hour': 'Hour of day to run scheduled processing (0-23, 24-hour format)',
            'schedule_minute': 'Minute of hour to run scheduled processing (0-59)',
        }

