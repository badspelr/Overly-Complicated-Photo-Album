# Visual Guide: Auto Process on Upload (Future Feature)

## Admin Panel Appearance

When you visit: `http://localhost:8000/admin/album/aiprocessingsettings/1/change/`

You'll see:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Change AI processing settings                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│ ┌──── Processing Modes ──────────────────────────────────────────┐ │
│ │                                                                  │ │
│ │ ╔═══════════════════════════════════════════════════════════╗  │ │
│ │ ║ ⚠️ Note: Auto Process on Upload is a FUTURE FEATURE and   ║  │ │
│ │ ║ currently disabled. Use Scheduled Processing below for     ║  │ │
│ │ ║ automatic AI processing.                                   ║  │ │
│ │ ╚═══════════════════════════════════════════════════════════╝  │ │
│ │                                                                  │ │
│ │ Control when AI processing occurs                                │ │
│ │                                                                  │ │
│ │ ☐ 🚧 Auto Process on Upload (Future Feature) [DISABLED]        │ │
│ │                                                                  │ │
│ │   FUTURE FEATURE - Not yet implemented.                         │ │
│ │   This feature will automatically process photos/videos with    │ │
│ │   AI when uploaded. Currently disabled. Use Scheduled           │ │
│ │   Processing or manual processing instead.                      │ │
│ │                                                                  │ │
│ │ ☑ Scheduled Processing                                          │ │
│ │                                                                  │ │
│ │   Enable scheduled batch processing of pending items            │ │
│ │                                                                  │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌──── Batch Processing Settings ─────────────────────────────────┐ │
│ │ Configure batch processing parameters                            │ │
│ │                                                                  │ │
│ │ Batch size: [500]                                               │ │
│ │ Maximum number of items to process per scheduled run            │ │
│ │                                                                  │ │
│ │ Processing timeout: [30]                                        │ │
│ │ Timeout in seconds for processing each item                     │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌──── Permission Limits ─────────────────────────────────────────┐ │
│ │ Set limits for album admins (site admins have no limits)        │ │
│ │                                                                  │ │
│ │ Album admin processing limit: [50]                              │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ ┌──── Schedule Configuration ────────────────────────────────────┐ │
│ │ Set the time for scheduled batch processing (24-hour format)    │ │
│ │                                                                  │ │
│ │ Schedule hour: [2]                                              │ │
│ │ Hour of the day (0-23) to run scheduled processing              │ │
│ │                                                                  │ │
│ │ Schedule minute: [0]                                            │ │
│ │ Minute of the hour (0-59) to run scheduled processing           │ │
│ └──────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│ [Save]                                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Visual Elements

### 1. Warning Banner (Yellow Background)
```
╔═══════════════════════════════════════════════════════════╗
║ ⚠️ Note: Auto Process on Upload is a FUTURE FEATURE and   ║
║ currently disabled. Use Scheduled Processing below for     ║
║ automatic AI processing.                                   ║
╚═══════════════════════════════════════════════════════════╝
```
- Background: Light yellow (#fef3cd)
- Border: Yellow left border (#ffc107)
- Makes it immediately obvious this is informational

### 2. Disabled Checkbox
```
☐ 🚧 Auto Process on Upload (Future Feature) [DISABLED]
```
- Checkbox is grayed out and unclickable
- 🚧 emoji indicates "under construction"
- "[DISABLED]" suffix makes status clear
- Mouse hover shows: "Future Feature - Not yet implemented"

### 3. Enhanced Help Text
```
FUTURE FEATURE - Not yet implemented.
This feature will automatically process photos/videos with AI when 
uploaded. Currently disabled. Use Scheduled Processing or manual 
processing instead.
```
- Bold "FUTURE FEATURE" text
- Gray color to indicate inactive
- Clear instructions on alternatives

## Browser Rendering

In your browser, it will look like:

**Field Label:**
🚧 Auto Process on Upload (Future Feature)

**Checkbox:**
□ (grayed out, cannot click)

**Help Text Below:**
**FUTURE FEATURE - Not yet implemented.**  
This feature will automatically process photos/videos with AI when uploaded. Currently disabled. Use **Scheduled Processing** or manual processing instead.

## What Users See

### Behavior:
1. ✅ Field is visible (not hidden)
2. ✅ Clearly marked as future feature
3. ✅ Cannot be toggled on
4. ✅ Clicking does nothing
5. ✅ Hover shows disabled tooltip
6. ✅ Help text explains alternatives

### User Experience:
- **Transparent** - Users know it exists but isn't ready
- **Not confusing** - Clear "FUTURE FEATURE" label
- **Helpful** - Directs to working alternatives
- **Professional** - Doesn't hide unfinished features

## Code That Creates This

### Model (album/models.py)
```python
auto_process_on_upload = models.BooleanField(
    default=False,
    help_text="[FUTURE FEATURE] Automatically process photos/videos..."
)
```

### Admin Form (album/admin.py)
```python
class AIProcessingSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auto_process_on_upload'].disabled = True
        self.fields['auto_process_on_upload'].label = '🚧 Auto Process on Upload (Future Feature)'
```

### Fieldset Description (album/admin.py)
```python
fieldsets = (
    ('Processing Modes', {
        'description': (
            '<div style="background: #fef3cd; border-left: 4px solid #ffc107; '
            'padding: 10px; margin-bottom: 15px;">'
            '<strong>ℹ️ Note:</strong> Auto Process on Upload is a '
            '<strong>future feature</strong> and currently disabled...'
        )
    }),
)
```

## Testing the Changes

1. **Visit admin page:**
   ```
   http://localhost:8000/admin/album/aiprocessingsettings/1/change/
   ```

2. **Check these elements:**
   - [ ] Yellow warning banner appears at top of Processing Modes
   - [ ] Checkbox has 🚧 icon in label
   - [ ] Checkbox is grayed out (disabled)
   - [ ] Clicking checkbox does nothing
   - [ ] Help text says "FUTURE FEATURE"
   - [ ] Help text suggests alternatives (Scheduled Processing)

3. **Try to enable it:**
   - Click the checkbox → Nothing happens
   - Click Save → Setting remains False
   - Check database → Still False

4. **Verify other settings work:**
   - Toggle "Scheduled Processing" → Should work
   - Change batch size → Should work
   - Save → Other settings should save normally

## Database State

```bash
# Check the setting
docker-compose exec web python manage.py shell

>>> from album.models import AIProcessingSettings
>>> s = AIProcessingSettings.load()
>>> s.auto_process_on_upload
False  # ← Always False

>>> s.scheduled_processing
True   # ← Can be True or False (works normally)
```

## Summary

✅ **What Changed:**
- Field now defaults to False
- Field is disabled in admin form
- Visual indicators added (🚧 icon, warning banner)
- Help text updated to say "FUTURE FEATURE"
- Documentation created

✅ **What Didn't Change:**
- Field still exists in database
- Field still appears in admin
- Other AI settings work normally
- No impact on existing functionality

✅ **Result:**
- Clear communication that feature isn't ready
- Users aren't confused
- Admin panel remains professional
- Easy to enable when feature is implemented

---

**To see it in action:** Visit `http://localhost:8000/admin/album/aiprocessingsettings/1/change/` and login as admin.
