#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'photo_album.settings')
django.setup()

from album.admin import UserAdmin
from album.admin_site import custom_admin_site
from django.contrib.auth.models import User

print('UserAdmin class loaded')
print('Has get_actions method:', hasattr(UserAdmin, 'get_actions'))
print('Has send_email_to_users method:', hasattr(UserAdmin, 'send_email_to_users'))

registered_admin = custom_admin_site._registry.get(User)
print('\nUser model registered:', registered_admin is not None)
print('Registered admin class:', type(registered_admin).__name__)

# Create a test instance and check
from django.test import RequestFactory
from django.contrib.auth import get_user_model

rf = RequestFactory()
req = rf.get('/admin/')
User = get_user_model()
req.user = User.objects.filter(is_superuser=True).first()

if req.user:
    actions = registered_admin.get_actions(req)
    print('\nAvailable actions:')
    for action_name in actions.keys():
        print(f'  - {action_name}')
