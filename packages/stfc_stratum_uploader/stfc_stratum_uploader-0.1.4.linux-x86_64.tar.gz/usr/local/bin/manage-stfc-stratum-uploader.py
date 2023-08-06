#!/usr/bin/python
import logging
import os
import sys

logger = logging.getLogger(__name__)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archer.settings')

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')
        os.environ.setdefault('REUSE_DB', '1')
    else:
        os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

    logger.debug('DJANGO_SETTINGS_MODULE = %s' % os.environ['DJANGO_SETTINGS_MODULE'])
    logger.debug('DJANGO_CONFIGURATION = %s' % os.environ['DJANGO_CONFIGURATION'])

    import configurations.importer
    configurations.importer.install()

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
