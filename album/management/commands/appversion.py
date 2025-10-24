"""
Management command to display version information.
"""

from django.core.management.base import BaseCommand
from photo_album.__version__ import (
    __version__,
    __version_info__,
    __title__,
    __author__,
    __license__,
    __copyright__,
    __url__,
    __release_date__,
    __status__,
    VERSION_HISTORY,
)


class Command(BaseCommand):
    help = 'Display Django Photo Album version information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--short',
            action='store_true',
            help='Display only the version number',
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='Display version history',
        )

    def handle(self, *args, **options):
        if options['short']:
            self.stdout.write(__version__)
            return

        if options['history']:
            self.display_history()
            return

        self.display_full_info()

    def display_full_info(self):
        """Display complete version information."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS(f' {__title__}'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        self.stdout.write(f'\n  Version:        {__version__}')
        self.stdout.write(f'  Release Date:   {__release_date__}')
        self.stdout.write(f'  Status:         {__status__}')
        self.stdout.write(f'  Author:         {__author__}')
        self.stdout.write(f'  License:        {__license__}')
        self.stdout.write(f'  Repository:     {__url__}')
        
        self.stdout.write('\n' + '-'*70)
        self.stdout.write('  Current Release Highlights:')
        self.stdout.write('-'*70)
        
        current_version = VERSION_HISTORY.get(__version__, {})
        if current_version:
            for highlight in current_version.get('highlights', []):
                self.stdout.write(f'  • {highlight}')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('  Ready for production deployment! 🚀'))
        self.stdout.write('='*70 + '\n')

    def display_history(self):
        """Display version history."""
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS(' Version History'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        for version in sorted(VERSION_HISTORY.keys(), reverse=True):
            info = VERSION_HISTORY[version]
            self.stdout.write(self.style.WARNING(f'\n[{version}] - {info["date"]}'))
            self.stdout.write(f'  Name: {info["name"]}')
            self.stdout.write('  Highlights:')
            for highlight in info['highlights']:
                self.stdout.write(f'    • {highlight}')
        
        self.stdout.write('\n' + '='*70 + '\n')
