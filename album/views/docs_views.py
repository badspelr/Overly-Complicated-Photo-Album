"""
Documentation views for Django admin.
Renders markdown documentation files as HTML in the admin interface.
"""

import os
from pathlib import Path
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
import markdown
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension


@staff_member_required
def documentation_index(request):
    """Display documentation index page."""
    docs_structure = {
        'Getting Started': [
            {'title': 'README - Project Overview', 'file': 'README.md'},
            {'title': '⭐ Getting Started with Docker', 'file': 'docs/deployment/GETTING_STARTED_DOCKER.md'},
        ],
        'Deployment & Docker': [
            {'title': '⭐ Complete Docker Setup Guide', 'file': 'docs/deployment/DOCKER_SETUP.md'},
            {'title': '🌐 Nginx Setup & Configuration', 'file': 'docs/deployment/NGINX_SETUP.md'},
            {'title': '🌍 Virtual Domains Setup', 'file': 'docs/deployment/VIRTUAL_DOMAINS_SETUP.md'},
            {'title': 'Docker Hub Publishing', 'file': 'docs/deployment/DOCKER_HUB_PUBLISHING.md'},
            {'title': 'Docker Overview', 'file': 'docs/deployment/DOCKER.md'},
            {'title': 'Docker README', 'file': 'docs/deployment/DOCKER_README.md'},
            {'title': 'Docker Quick Reference', 'file': 'docs/deployment/DOCKER_QUICK_REFERENCE.md'},
            {'title': 'Docker Dev vs Prod', 'file': 'docs/deployment/DOCKER_DEV_VS_PROD.md'},
            {'title': 'Docker Migration Summary', 'file': 'docs/deployment/DOCKER_MIGRATION_SUMMARY.md'},
            {'title': 'Docker Migration Checklist', 'file': 'docs/deployment/DOCKER_MIGRATION_CHECKLIST.md'},
            {'title': 'Docker Requirements Explained', 'file': 'docs/deployment/DOCKER_REQUIREMENTS_EXPLAINED.md'},
            {'title': 'Docker Health Check Fix', 'file': 'docs/deployment/DOCKER_HEALTH_CHECK_FIX.md'},
            {'title': 'Celery & Background Tasks', 'file': 'docs/deployment/CELERY_DOCKER_SETUP.md'},
            {'title': 'Celery Production Validation', 'file': 'docs/deployment/CELERY_PRODUCTION_VALIDATION.md'},
            {'title': 'Virtual Environment in Docker', 'file': 'docs/deployment/VENV_IN_DOCKER_EXPLAINED.md'},
            {'title': 'Production Quick Start', 'file': 'docs/deployment/PRODUCTION_QUICK_START.md'},
            {'title': 'Deployment Checklist', 'file': 'docs/deployment/DEPLOYMENT_CHECKLIST.md'},
            {'title': 'Deployment Cheat Sheet', 'file': 'docs/deployment/DEPLOYMENT_CHEAT_SHEET.md'},
            {'title': 'Deployment with Systemd', 'file': 'docs/deployment/DEPLOYMENT_SYSTEMD.md'},
        ],
        'Administration & Configuration': [
            {'title': '⭐ Production Readiness Assessment', 'file': 'docs/admin-guides/PRODUCTION_READINESS_ASSESSMENT.md'},
            {'title': 'GPU Setup Guide', 'file': 'docs/admin-guides/GPU_SETUP.md'},
            {'title': 'Email Configuration', 'file': 'docs/admin-guides/EMAIL_CONFIGURATION.md'},
            {'title': 'Invitation Email Customization', 'file': 'docs/admin-guides/INVITATION_EMAIL_CUSTOMIZATION.md'},
        ],
        'Development & Testing': [
            {'title': 'Test Suite Status', 'file': 'docs/development/TEST_SUITE_STATUS_UPDATE.md'},
            {'title': 'Test Coverage Analysis', 'file': 'docs/development/TEST_COVERAGE_ANALYSIS.md'},
            {'title': 'Test Execution Results', 'file': 'docs/development/TEST_EXECUTION_RESULTS.md'},
            {'title': 'Remaining Test Issues', 'file': 'docs/development/REMAINING_TEST_ISSUES_EXPLAINED.md'},
            {'title': 'Requirements Cleanup', 'file': 'docs/development/REQUIREMENTS_CLEANUP.md'},
            {'title': 'Requirements Review', 'file': 'docs/development/REQUIREMENTS_REVIEW.md'},
        ],
        'Features': [
            {'title': '📚 Admin Documentation Feature', 'file': 'docs/features/ADMIN_DOCUMENTATION_FEATURE.md'},
            {'title': '🔐 Registration Control', 'file': 'docs/features/REGISTRATION_CONTROL.md'},
        ],
        'Reference': [
            {'title': 'Changelog', 'file': 'CHANGELOG.md'},
        ],
        'Completed Tasks (Archive)': [
            {'title': 'View All Completed Tasks →', 'file': 'docs/archive/completed-tasks/README.md'},
        ],
    }
    
    context = {
        'title': 'Documentation',
        'docs_structure': docs_structure,
    }
    return render(request, 'admin/documentation_index.html', context)


@staff_member_required
def documentation_view(request, filename):
    """Display a specific documentation file as HTML."""
    # Security: only allow markdown files
    if not filename.endswith('.md'):
        raise Http404("Invalid file type")
    
    # Allow subdirectories but prevent directory traversal
    if '..' in filename or filename.startswith('/'):
        raise Http404("Invalid filename")
    
    # Normalize path separators
    filename = filename.replace('\\', '/')
    
    # Get the base directory (project root)
    base_dir = Path(__file__).resolve().parent.parent.parent
    file_path = base_dir / filename
    
    # Security: ensure the resolved path is still within the project
    try:
        file_path = file_path.resolve()
        base_dir = base_dir.resolve()
        if not str(file_path).startswith(str(base_dir)):
            raise Http404("Invalid file path")
    except Exception:
        raise Http404("Invalid file path")
    
    if not file_path.exists():
        raise Http404(f"Documentation file not found: {filename}")
    
    # Read the markdown file
    with open(file_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert markdown to HTML with extensions
    md = markdown.Markdown(extensions=[
        TocExtension(title='Table of Contents'),
        CodeHiliteExtension(css_class='highlight', linenums=False),
        FencedCodeExtension(),
        'tables',
        'nl2br',
    ])
    html_content = md.convert(markdown_content)
    
    # Get the title from the first H1 or use filename
    title = filename.split('/')[-1].replace('.md', '').replace('_', ' ').title()
    if markdown_content.startswith('# '):
        title = markdown_content.split('\n')[0].replace('# ', '')
    
    context = {
        'title': title,
        'filename': filename,
        'content': html_content,
        'toc': md.toc if hasattr(md, 'toc') else '',
    }
    return render(request, 'admin/documentation_view.html', context)
