"""
Custom Django Admin Site with Documentation Link
"""
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


class CustomAdminSite(admin.AdminSite):
    site_header = "Photo Album Administration"
    site_title = "Photo Album Admin"
    index_title = "Welcome to Photo Album Administration"
    
    def each_context(self, request):
        """Add custom context variables to every admin page"""
        context = super().each_context(request)
        context['documentation_url'] = reverse('album:documentation_index')
        return context


# Create custom admin site instance
custom_admin_site = CustomAdminSite(name='custom_admin')
