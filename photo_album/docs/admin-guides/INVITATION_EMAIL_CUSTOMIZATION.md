# Customizing Invitation Emails

## Overview

The invitation email system has been improved to use **editable templates** instead of hardcoded text. You can now easily customize both the plain text and HTML versions of invitation emails.

## Email Templates Location

The invitation email templates are located in:

```
album/templates/album/emails/
├── invitation_email.txt    # Plain text version
└── invitation_email.html   # HTML version (styled)
```

## Available Variables

When editing the templates, you can use these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{{ inviter_name }}` | Username of person sending invitation | `amandanielsen221@gmail.com` |
| `{{ album_titles }}` | Comma-separated list of album names | `Evan Videos, Evan Photos` |
| `{{ site_url }}` | Full URL to your site | `http://localhost:8000/` |

## Plain Text Template

**File:** `album/templates/album/emails/invitation_email.txt`

This is what recipients see if their email client doesn't support HTML:

```
Hello!

{{ inviter_name }} has invited you to view their photo albums: {{ album_titles }}.

Please register at {{ site_url }} to access the albums.

You can create an account and start viewing these albums right away!

Best regards,
{{ inviter_name }}

---
Photo Album System
{{ site_url }}
```

### Customization Ideas:
- Add your organization name
- Include support contact information
- Add instructions for first-time users
- Include app download links (for future Android app)

## HTML Template

**File:** `album/templates/album/emails/invitation_email.html`

This is what most recipients see - a nicely formatted HTML email with:
- Green header with camera emoji
- Styled content area
- Highlighted album list
- Green "Register & View Albums" button
- Footer with system information

### Customization Options:

**1. Change Colors:**
```css
.header {
    background-color: #4CAF50;  /* Change to your brand color */
}
.button {
    background-color: #4CAF50;  /* Match your brand */
}
```

**2. Add Your Logo:**
```html
<div class="header">
    <img src="https://yoursite.com/logo.png" alt="Logo" style="max-width: 150px;">
    <h1>📸 Album Invitation</h1>
</div>
```

**3. Change Greeting:**
```html
<p>Hi there!</p>  <!-- Instead of "Hello!" -->
```

**4. Add More Information:**
```html
<div class="album-list">
    <strong>Albums:</strong> {{ album_titles }}
    <p><small>{{ albums|length }} album(s) shared</small></p>
</div>
```

**5. Add Social Links:**
```html
<div class="footer">
    <p>Photo Album System</p>
    <p>
        <a href="https://facebook.com/yourpage">Facebook</a> | 
        <a href="https://twitter.com/yourpage">Twitter</a>
    </p>
</div>
```

## How to Edit

### Method 1: Direct File Editing (Requires Container Restart)

1. Edit the template files locally
2. Restart the web container:
   ```bash
   docker-compose restart web
   ```

### Method 2: Edit Inside Docker (No Restart Needed)

```bash
docker exec -it photo_album_web nano album/templates/album/emails/invitation_email.txt
```

Changes take effect immediately (Django reloads templates in DEBUG mode).

## Testing Your Changes

### View Email in Logs

Since you're in DEBUG mode, emails print to console:

```bash
# Send a test invitation, then view the logs
docker-compose logs -f web | grep -A 50 "Subject: Invitation"
```

### Send a Test Email

1. Go to http://localhost:8000/users/invite/
2. Enter your own email address
3. Select some albums
4. Click "Invite User"
5. Check Docker logs to see the email

### Test with Django Shell

```bash
docker exec -it photo_album_web python manage.py shell
```

Then run:
```python
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

context = {
    'inviter_name': 'TestUser',
    'album_titles': 'Summer Vacation, Family Photos',
    'site_url': 'http://localhost:8000/',
}

text = render_to_string('album/emails/invitation_email.txt', context)
html = render_to_string('album/emails/invitation_email.html', context)

print("=== PLAIN TEXT ===")
print(text)
print("\n=== HTML ===")
print(html)

# Actually send test email (requires SMTP configured)
email = EmailMultiAlternatives(
    'Test Invitation',
    text,
    settings.DEFAULT_FROM_EMAIL,
    ['your-email@example.com']
)
email.attach_alternative(html, "text/html")
email.send()
```

## Advanced Customization

### Add Custom Subject Line

Edit `album/views/user_views.py` line ~183:

```python
# Before:
subject = 'Invitation to view albums'

# After:
subject = f'{request.user.username} shared albums with you!'
# or
subject = f'📸 You have been invited to view {len(albums)} album(s)'
```

### Include Album Count

Add to context in `album/views/user_views.py` line ~189:

```python
context = {
    'inviter_name': request.user.username,
    'album_titles': album_titles,
    'site_url': request.build_absolute_uri('/'),
    'album_count': len(albums),  # Add this
}
```

Then use in template:
```
{{ inviter_name }} has shared {{ album_count }} album(s) with you!
```

### Add Inviter's Full Name

Modify context:
```python
context = {
    'inviter_name': request.user.get_full_name() or request.user.username,
    'inviter_email': request.user.email,
    # ... rest
}
```

Use in template:
```
Best regards,
{{ inviter_name }}
{{ inviter_email }}
```

## Email Preview (What Recipients See)

### Plain Text Version:
```
Hello!

amandanielsen221@gmail.com has invited you to view their photo albums: Evan Videos, Evan Photos.

Please register at http://localhost:8000/ to access the albums.

You can create an account and start viewing these albums right away!

Best regards,
amandanielsen221@gmail.com

---
Photo Album System
http://localhost:8000/
```

### HTML Version:
A nicely formatted email with:
- Green header with camera emoji 📸
- White content area on gray background
- Green-bordered box showing album names
- Green "Register & View Albums" button
- Professional footer

## Best Practices

1. **Keep it Simple** - Don't overwhelm recipients with too much text
2. **Clear Call-to-Action** - Make it obvious what they should do next
3. **Mobile Friendly** - Keep width under 600px
4. **Test Both Versions** - Some email clients only show plain text
5. **Brand Consistency** - Match your website's colors and style
6. **Include Unsubscribe** - If sending bulk invitations (future feature)

## Common Customizations

### Make it More Formal:
```
Dear Recipient,

You have been invited to access photo albums...

Sincerely,
The Photo Album Team
```

### Make it More Casual:
```
Hey! 👋

{{ inviter_name }} wants to share some awesome photos with you!

Check them out: {{ album_titles }}

Click here to get started! 🚀
```

### Add Instructions:
```
How to get started:
1. Click the button below
2. Create a free account
3. Start viewing your shared albums!
```

## Files Modified

- ✅ Created: `album/templates/album/emails/invitation_email.txt`
- ✅ Created: `album/templates/album/emails/invitation_email.html`
- ✅ Updated: `album/views/user_views.py` - Now uses templates instead of hardcoded text
- ✅ Updated: Emails now sent with both text and HTML versions

## Date
October 22, 2025
