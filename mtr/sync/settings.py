import os

from django.conf import settings

# custom prefix for avoiding name colissions
PREFIX = getattr(settings, 'MTR_SYNC_SETTINGS_PREFIX', 'MTR_SYNC')


def getattr_with_prefix(name, default):
    """Shortcut for getting settings attribute with prefix"""

    return lambda: getattr(settings, '{}_{}'.format(PREFIX, name), default)


def get_buffer_file_path(instance, filename, relative=False):
    """Generate file path for report"""

    path = os.path.join(settings.MEDIA_ROOT,
        'sync', instance.get_action_display().lower(),
        filename.lower())

    if relative:
        path = path.split(settings.MEDIA_ROOT)[1].lstrip('/')

    return path

# used to generate custom file path
FILE_PATH = getattr_with_prefix('FILE_PATH', get_buffer_file_path)

# theme path
THEME_PATH = getattr_with_prefix('THEME_PATH', 'default')

# additional api for import and export to register
IMPORT_PROCESSORS = getattr_with_prefix('IMPORT_PROCESSORS', [
    'mtr.sync.api.processors.xls',
    'mtr.sync.api.processors.xlsx',
])

# model attribute where settings placed
MODEL_SETTINGS_NAME = getattr_with_prefix(
    'MODEL_SETTINGS_NAME', 'sync_settings')

# limit preview of data on settings page
LIMIT_PREVIEW = getattr_with_prefix('LIMIT_PREVIEW', 20)
