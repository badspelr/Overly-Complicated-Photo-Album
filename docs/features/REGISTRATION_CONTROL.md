# User Registration Control Feature

This feature allows administrators to enable or disable public user registration through the Django admin panel.

## Overview

The registration control feature provides a simple toggle in the Django admin to:
- **Enable/Disable new user registration**
- **Hide registration links** when disabled (login page, homepage)
- **Show friendly error message** if users try to access the registration URL directly
- **Keep existing users unaffected** - only blocks new registrations

## How to Use

### Enabling/Disabling Registration

1. **Log into Django Admin** at `/admin/`
2. **Click "Site Settings"** in the left sidebar
3. **Edit the settings** (there's only one Site Settings object)
4. **Toggle "Allow registration"** checkbox:
   - ✅ **Checked** = Users can register new accounts (default)
   - ❌ **Unchecked** = Registration is disabled
5. **Click "Save"**

Changes take effect immediately - no server restart needed.

### What Happens When Registration is Disabled

**On the Login Page:**
- The "Don't have an account? Sign Up" link disappears
- Users only see the login form and password reset link

**On the Homepage:**
- The "Sign Up" button is hidden for anonymous users
- Only the "Login" button is shown

**If Someone Tries to Access `/register/` Directly:**
- They're redirected to the login page
- An error message appears: "Registration is currently disabled. Please contact the administrator."

**Existing Users:**
- Can still log in normally
- No changes to their accounts or permissions
- All existing functionality works the same

## Use Cases

### When to Disable Registration

1. **Private/Invitation-Only Site**
   - You want to manually create accounts
   - Use the "Invite User" feature instead

2. **Temporary Closure**
   - Performing maintenance
   - Dealing with spam issues
   - Waiting for approval/resources

3. **Capacity Management**
   - Server resources limited
   - Storage quota concerns
   - Want to control user growth

4. **Beta/Testing Period**
   - Limited user testing phase
   - Controlled rollout

### When to Enable Registration

1. **Public Photo Sharing Site**
   - Open to anyone who wants to join
   - Default setting for most installations

2. **Community Platform**
   - Want organic user growth
   - Self-service account creation

## Technical Details

### Database Field

Added to the `SiteSettings` model:

```python
allow_registration = models.BooleanField(
    default=True, 
    help_text='Allow new users to register. Uncheck to disable public registration.'
)
```

### View Protection

The `register` view checks the setting before allowing registration:

```python
def register(request):
    """Register a new user."""
    # Check if registration is allowed
    site_settings = SiteSettings.get_settings()
    if not site_settings.allow_registration:
        messages.error(request, 'Registration is currently disabled. Please contact the administrator.')
        return redirect('login')
    # ... rest of registration logic
```

### Template Conditionals

Registration links are conditionally displayed:

```django
{% if site_settings.allow_registration %}
    <a href="{% url 'album:register' %}">Sign Up</a>
{% endif %}
```

The `site_settings` context is available in all templates via the `site_settings` context processor.

### Singleton Pattern

`SiteSettings` uses a singleton pattern - only one instance exists:

```python
@classmethod
def get_settings(cls):
    """Get or create the singleton settings instance."""
    settings, created = cls.objects.get_or_create(pk=1)
    return settings
```

This ensures consistent settings across the entire application.

## Admin Configuration

The admin interface includes:

1. **Clear Field Grouping**
   - "Basic Settings" section (title, description)
   - "Registration Settings" section (allow_registration)

2. **Helpful Description**
   - Field help text explains the purpose
   - Section description provides context

3. **Protection**
   - Cannot create multiple SiteSettings instances
   - Cannot delete the SiteSettings object
   - Prevents accidental misconfiguration

## Migration

The feature was added in migration `0008_add_registration_toggle.py`:

```bash
# Create migration
docker-compose exec web python manage.py makemigrations --name add_registration_toggle

# Apply migration
docker-compose exec web python manage.py migrate
```

Default value is `True` (registration enabled) to maintain backward compatibility.

## Alternative: Invitation-Only System

If registration is disabled, you can still add users via:

### 1. Django Admin
- Navigate to Users → Add User
- Create account manually

### 2. Invitation System
- Use the built-in "Invite User" feature
- Sends email invitation with setup link
- Available at `/album/invite/`

### 3. Management Command
```bash
docker-compose exec web python manage.py createsuperuser
```

## Security Considerations

1. **No Bypass**
   - Direct URL access is blocked
   - API endpoints respect the setting (if implemented)

2. **Admin Control**
   - Only staff members can change the setting
   - Logged in audit trail

3. **Clear Communication**
   - Users see a friendly error message
   - Explains why registration is unavailable

4. **No Data Exposure**
   - Setting doesn't affect existing users
   - No security implications for current accounts

## Testing

### Test Registration Disabled

1. Go to Admin → Site Settings
2. Uncheck "Allow registration"
3. Save
4. Log out
5. Try to access `/register/` → Should redirect to login with error
6. Check login page → "Sign Up" link should be hidden
7. Check homepage → "Sign Up" button should be hidden

### Test Registration Enabled

1. Go to Admin → Site Settings
2. Check "Allow registration"
3. Save
4. Log out
5. Access `/register/` → Should show registration form
6. Check login page → "Sign Up" link should appear
7. Check homepage → "Sign Up" button should appear

## Future Enhancements

Possible future additions:

1. **Registration Approval Workflow**
   - Users can register but accounts need approval
   - Admin receives notification
   - Users get activation email after approval

2. **Invite-Only Mode**
   - Users can only register with invitation code
   - Track which invites are used

3. **Rate Limiting**
   - Limit registrations per time period
   - Prevent spam/abuse

4. **Custom Registration Message**
   - Admin can set custom message when disabled
   - Explain when registration will reopen

5. **Scheduled Enable/Disable**
   - Automatically enable/disable at certain times
   - Useful for timed rollouts

## Related Features

- **User Invitations** - Alternative to public registration
- **User Management** - Admin can manually create users
- **Terms of Conduct** - Registration requires terms acceptance
- **User Profiles** - Track registration details and IP

## Support

If you encounter issues:

1. Check admin logs for errors
2. Verify Site Settings object exists
3. Clear browser cache
4. Check Django logs: `docker-compose logs web`

For questions or bug reports, see the main documentation.
