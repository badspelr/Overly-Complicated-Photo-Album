# Auto Process on Upload - Future Feature

## Status: 🚧 Not Yet Implemented

### Overview

The "Auto Process on Upload" feature in AI Processing Settings is currently **disabled** and marked as a **future feature**. This setting appears in the Django admin panel but is non-functional.

### Current Behavior

- **Field is disabled** - Cannot be toggled on
- **Default value: False** - Always off
- **Visual indicator** - Marked with 🚧 icon in admin panel
- **Help text** - Clearly states "FUTURE FEATURE"
- **Warning banner** - Admin page shows notice about feature status

### What This Feature Would Do (When Implemented)

When fully implemented, this feature would:

1. **Automatic Processing** - Process photos/videos with AI immediately upon upload
2. **Real-time Analysis** - Generate AI descriptions, tags, embeddings instantly
3. **Seamless Experience** - No manual processing or scheduled batch runs needed

### Why It's Disabled

- **Performance Impact** - Could slow down uploads significantly
- **Resource Management** - Needs careful queue management
- **User Experience** - Requires background task optimization
- **Testing Required** - Needs extensive testing with various file sizes

### Current Alternatives

Use these working methods instead:

#### 1. Scheduled Processing (Recommended)
- **Enable:** AI Processing Settings → "Scheduled Processing" = ✅
- **Configure:** Set batch size and schedule time (default: 2:00 AM)
- **Automatic:** Runs daily, processes pending items
- **Efficient:** Batch processing is optimized

#### 2. Manual Processing
**For Photos:**
- Go to album detail page
- Click "Process Photos AI" button
- Select batch size
- Click "Start Processing"

**For Videos:**
- Go to album detail page
- Click "Process Videos AI" button
- Select batch size
- Click "Start Processing"

### Implementation Roadmap

When we implement this feature, it will require:

#### Phase 1: Infrastructure (1-2 weeks)
- [ ] Celery task queue optimization
- [ ] Redis job prioritization
- [ ] Upload progress tracking
- [ ] Background task monitoring

#### Phase 2: Implementation (1-2 weeks)
- [ ] Post-upload signal handler
- [ ] Async task creation on upload
- [ ] Queue management logic
- [ ] Rate limiting for concurrent uploads

#### Phase 3: Testing (1 week)
- [ ] Unit tests for upload signals
- [ ] Integration tests for task queue
- [ ] Load testing with multiple uploads
- [ ] Error handling and retry logic

#### Phase 4: Optimization (1 week)
- [ ] Batch grouping for uploads
- [ ] Priority queue implementation
- [ ] Resource throttling
- [ ] User feedback indicators

**Total Estimated Effort:** 4-6 weeks

### Technical Details

#### Current Signal Handler Location
`album/signals.py` - Post-save signals for Photo and Video models

#### Required Changes
```python
# album/signals.py (future implementation)
@receiver(post_save, sender=Photo)
def auto_process_photo(sender, instance, created, **kwargs):
    """Process photo with AI if auto-processing is enabled"""
    if created:
        settings = AIProcessingSettings.load()
        if settings.auto_process_on_upload:
            # Queue for processing
            from album.tasks import process_single_photo_task
            process_single_photo_task.delay(instance.id)
```

#### Dependencies
- Celery worker must be running
- Redis must be available
- AI models must be loaded
- Sufficient memory/GPU resources

### Configuration

In Django Admin → AI Processing Settings:

```
Processing Modes:
┌─────────────────────────────────────────────────────┐
│ ⚠️ Note: Auto Process on Upload is a FUTURE        │
│    FEATURE and currently disabled. Use Scheduled    │
│    Processing below for automatic AI processing.    │
└─────────────────────────────────────────────────────┘

☐ 🚧 Auto Process on Upload (Future Feature)
   FUTURE FEATURE - Not yet implemented.
   This feature will automatically process photos/videos 
   with AI when uploaded. Currently disabled. Use 
   Scheduled Processing or manual processing instead.

☑ Scheduled Processing
   Enable scheduled batch processing of pending items
```

### FAQ

#### Q: Why can't I enable this feature?
**A:** It's not yet implemented. The UI element exists for future development but is non-functional.

#### Q: When will this be available?
**A:** No specific timeline yet. It's on the roadmap (see TODO_REVIEW.md, Medium Priority item #10).

#### Q: Will my photos be processed automatically?
**A:** Not on upload. Use Scheduled Processing (runs daily) or manual processing instead.

#### Q: Can I help implement this?
**A:** Yes! See CONTRIBUTING.md for guidelines. This is a great intermediate-difficulty feature.

#### Q: What happens if I check the box?
**A:** Nothing. The field is disabled in the admin form and won't accept changes.

### Related Documentation

- [AI Processing Settings Guide](../admin-guides/ADMIN_GUIDE_AI_SETTINGS.md)
- [Celery Setup](../deployment/CELERY.md)
- [Background Tasks](../technical/BACKGROUND_TASKS.md)
- [TODO Roadmap](../../TODO_REVIEW.md)

### Migration History

- **0008_add_registration_toggle.py** - Initial AI settings
- **0009_disable_auto_process_future_feature.py** - Marked as future feature, default to False

### Testing

To verify the feature is properly disabled:

```bash
# Check database value
docker-compose exec web python manage.py shell
>>> from album.models import AIProcessingSettings
>>> s = AIProcessingSettings.load()
>>> print(s.auto_process_on_upload)
False

# Upload a photo and verify it's NOT auto-processed
# 1. Upload a photo via web interface
# 2. Check photo detail page
# 3. Verify "Processing Status: Pending"
# 4. No automatic processing occurs
```

### Developer Notes

If you're implementing this feature:

1. **Start with signals** - `album/signals.py` post_save handlers
2. **Create task** - `album/tasks.py` new task function
3. **Add tests** - `album/tests/test_signals.py` and `album/tests/test_celery_tasks.py`
4. **Update admin** - Remove disabled state from form
5. **Document** - Update this file and admin guide
6. **Test thoroughly** - Upload queue management is critical

### Security Considerations

When implementing:

- **Rate limiting** - Prevent upload spam triggering excessive AI processing
- **Resource limits** - Cap concurrent processing tasks
- **User quotas** - Consider per-user processing limits
- **Abuse prevention** - Monitor for malicious bulk uploads
- **Error handling** - Failed processing shouldn't break uploads

---

**Last Updated:** October 24, 2025  
**Status:** Future Feature (Not Implemented)  
**Priority:** Medium (See TODO_REVIEW.md)  
**Estimated Implementation:** 4-6 weeks
