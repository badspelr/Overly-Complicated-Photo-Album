"""
User-related views.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.views import PasswordChangeView as DjangoPasswordChangeView, PasswordChangeDoneView as DjangoPasswordChangeDoneView
from django.utils import timezone
from ..models import Album, SiteSettings, UserProfile
from ..forms import UserInvitationForm, CustomUserChangeForm, CustomUserCreationForm, AdminUserChangeForm
from .base_views import AdminPermissionMixin, log_user_action

logger = logging.getLogger(__name__)


def register(request):
    """Register a new user."""
    # Check if registration is allowed
    site_settings = SiteSettings.get_settings()
    if not site_settings.allow_registration:
        messages.error(request, 'Registration is currently disabled. Please contact the administrator.')
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create user profile and record terms acceptance
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.terms_accepted = True
            profile.terms_accepted_date = timezone.now()
            
            # Get client IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            profile.terms_accepted_ip = ip
            profile.save()
            
            log_user_action('user_registered', user, 'registration', {'terms_accepted': True})
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    print(form)
    return render(request, 'registration/registration.html', {'form': form})


def terms_of_conduct(request):
    """Display Terms of Conduct page."""
    return render(request, 'album/terms_of_conduct.html')


def csam_policy(request):
    """Display CSAM Policy page."""
    return render(request, 'album/csam_policy.html')


def react_app(request):
    """Render the React application."""
    return render(request, 'album/react_app.html')


def homepage(request):
    """Homepage view."""
    settings = SiteSettings.objects.first()
    if not settings:
        settings = SiteSettings.objects.create()
    public_albums = Album.objects.filter(is_public=True).select_related('owner', 'category')
    return render(request, 'album/homepage.html', {
        'settings': settings, 
        'public_albums': public_albums
    })


@login_required
def user_manual(request):
    """Display the user manual."""
    return render(request, 'album/user_manual.html')

@login_required
def dashboard(request):
    """Render the dashboard page."""
    user_albums = Album.objects.filter(owner=request.user).prefetch_related('photos')
    has_owned_albums = user_albums.exists()
    context = {
        'user_albums': user_albums,
        'has_owned_albums': has_owned_albums,
    }
    return render(request, 'album/dashboard.html', context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile - users can only edit their own basic info, NOT groups."""
    model = User
    form_class = CustomUserChangeForm
    template_name = 'album/profile_edit.html'
    success_url = reverse_lazy('album:dashboard')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        # Note: removed is_active = True - users shouldn't control their active status
        user.save()
        log_user_action('profile_updated', self.request.user)
        messages.success(self.request, 'Your profile has been updated successfully')
        return super().form_valid(form)



@login_required
def invite_user(request):
    """Invite a user to view albums."""
    # Check permissions - site admins and album owners can invite users
    if not (request.user.is_site_admin or request.user.is_album_owner):
        messages.error(request, 'You do not have permission to invite users.')
        return redirect('album:dashboard')

    if request.method == 'POST':
        form = UserInvitationForm(request.POST, user=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            albums = form.cleaned_data['albums']
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Check if user already exists
            try:
                user = User.objects.get(email=email)
                # Add user as viewer to all selected albums
                for album in albums:
                    album.viewers.add(user)

                album_titles = ", ".join([album.title for album in albums])
                log_user_action('user_invited', request.user, 'albums', [album.id for album in albums])
                messages.success(request, f'User {user.username} has been added as a viewer to: {album_titles}')
            except User.DoesNotExist:
                # Only site admins can create new users
                if request.user.is_site_admin and username and password:
                    # Create new user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_active=form.cleaned_data.get('is_active', True)
                    )

                    # Assign selected groups or default to Viewer group
                    selected_groups = form.cleaned_data.get('groups')
                    if selected_groups:
                        user.groups.set(selected_groups)
                    else:
                        # Default to Viewer group if no groups selected
                        try:
                            viewer_group = Group.objects.get(name='Viewer')
                            user.groups.add(viewer_group)
                        except Group.DoesNotExist:
                            logger.warning("Viewer group does not exist - user created without group assignment")

                    user.save()

                    # Add user as viewer to all selected albums
                    for album in albums:
                        album.viewers.add(user)

                    group_names = ", ".join([group.name for group in user.groups.all()]) if user.groups.exists() else "No groups"
                    album_titles = ", ".join([album.title for album in albums])
                    log_user_action('user_created_and_invited', request.user, 'albums', [album.id for album in albums])
                    messages.success(request, f'User {user.username} has been created, assigned to groups: {group_names}, and added as a viewer to: {album_titles}')
                else:
                    # Send invitation email (for album admins or when no username/password provided)
                    album = albums.first() if albums else None
                    if album:
                        from django.template.loader import render_to_string
                        
                        subject = 'Invitation to view albums'
                        album_titles = ", ".join([album.title for album in albums])
                        
                        # Context for email templates
                        context = {
                            'inviter_name': request.user.username,
                            'album_titles': album_titles,
                            'site_url': request.build_absolute_uri('/'),
                        }
                        
                        # Render plain text and HTML versions
                        text_message = render_to_string('album/emails/invitation_email.txt', context)
                        html_message = render_to_string('album/emails/invitation_email.html', context)
                        
                        try:
                            # Send email with both text and HTML versions
                            email_msg = EmailMultiAlternatives(
                                subject,
                                text_message,
                                settings.DEFAULT_FROM_EMAIL,
                                [email]
                            )
                            email_msg.attach_alternative(html_message, "text/html")
                            email_msg.send()
                            
                            log_user_action('invitation_email_sent', request.user, 'albums', [album.id for album in albums])
                            messages.success(request, f'Invitation sent to {email} for albums: {album_titles}')
                        except Exception as e:
                            logger.error(f"Failed to send invitation email: {e}")
                            messages.error(request, 'Failed to send invitation email')

            return redirect('album:dashboard')
    else:
        form = UserInvitationForm(user=request.user)

    return render(request, 'album/invite_user.html', {
        'form': form,
        'can_create_users': request.user.is_site_admin
    })


@method_decorator(login_required, name='dispatch')
class ManageUsersView(LoginRequiredMixin, ListView):
    """Manage users (site admin only)."""
    model = User
    template_name = 'album/manage_users.html'
    context_object_name = 'users'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_site_admin:
            messages.error(request, 'You do not have permission to manage users.')
            return redirect('album:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Site admins can manage all users
        for user in context['users']:
            user.can_be_managed = True
        return context


# REMOVED: AlbumAdminUsersView - no longer needed since album admins are now per-album ownership based
# Album owners manage viewers through individual album management, not global user management


class UserEditView(LoginRequiredMixin, UpdateView):
    """Edit user details."""
    model = User
    template_name = 'album/edit_user.html'
    success_url = reverse_lazy('album:manage_users')
    context_object_name = 'edit_user'

    def dispatch(self, request, *args, **kwargs):
        # Only site admins can edit users directly
        if not request.user.is_site_admin:
            messages.error(request, 'You do not have permission to edit users.')
            return redirect('album:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_object(self, queryset=None):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])
        # Only site admins can edit any user
        return user

    def get_form_class(self):
        # Site admins get full user management capabilities
        return AdminUserChangeForm

    def form_valid(self, form):
        log_user_action('user_updated', self.request.user, 'user', self.object.id)
        messages.success(self.request, f'User {self.object.username} has been updated')
        return super().form_valid(form)


class UserDeleteView(AdminPermissionMixin, LoginRequiredMixin, DeleteView):
    """Delete user (admin only)."""
    model = User
    template_name = 'album/delete_user.html'
    success_url = reverse_lazy('album:manage_users')
    context_object_name = 'user_to_delete'

    def get_object(self, queryset=None):
        return get_object_or_404(User, pk=self.kwargs['user_id'])

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username

        # Prevent deletion of superuser accounts
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser accounts')
            return redirect('album:manage_users')

        # Prevent self-deletion
        if user == request.user:
            messages.error(request, 'You cannot delete your own account')
            return redirect('album:manage_users')

        # For Album Owners, only allow deletion of users who have access to their albums
        if request.user.is_album_owner and not request.user.is_superuser:
            # Check if the user to be deleted has access to any of the album owner's albums
            has_access = user.viewable_albums.filter(owner=request.user).exists()

            if not has_access:
                messages.error(request, 'You can only delete users who have access to your albums')
                return redirect('album:manage_users')

        log_user_action('user_deleted', request.user, 'user', user.id)
        messages.success(request, f'User {username} has been deleted successfully')
        return super().delete(request, *args, **kwargs)


class AppPasswordChangeView(LoginRequiredMixin, DjangoPasswordChangeView):
    """App-scoped password change view."""
    template_name = 'album/auth/password_change_form.html'
    success_url = reverse_lazy('album:password_change_done_app')


class AppPasswordChangeDoneView(LoginRequiredMixin, DjangoPasswordChangeDoneView):
    """App-scoped password change done view."""
    template_name = 'album/auth/password_change_done.html'


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """Allow users to delete their own account and all associated data."""
    model = User
    template_name = 'album/delete_account.html'
    success_url = '/'
    
    def get_object(self, queryset=None):
        # Users can only delete their own account
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get counts of data that will be deleted
        context.update({
            'albums_count': user.owned_albums.count(),
            'photos_count': sum(album.photos.count() for album in user.owned_albums.all()),
            'videos_count': sum(album.videos.count() for album in user.owned_albums.all()),
            'tags_count': user.tags.count(),
            'custom_albums_count': user.custom_albums.count(),
        })
        
        return context
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        
        # Log the account deletion
        log_user_action('account_deleted', user)
        logger.info(f"User {username} deleted their account and all associated data")
        
        # Add success message before logout
        messages.success(request, 'Your account and all associated data have been permanently deleted.')
        
        # Delete the user (CASCADE will handle related data)
        return super().delete(request, *args, **kwargs)