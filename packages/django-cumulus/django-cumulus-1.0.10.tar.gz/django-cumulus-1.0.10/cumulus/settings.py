import cloudfiles
from cloudfiles.consts import default_cdn_ttl

from django.conf import settings

CUMULUS = {
    'API_KEY': None,
    'AUTH_URL': 'us_authurl',
    'CNAMES': None,
    'CONTAINER': None,
    'SERVICENET': False,
    'TIMEOUT': 5,
    'TTL': default_cdn_ttl,  # 86400s (24h), python-cloudfiles default
    'USE_SSL': False,
    'USERNAME': None,
    'STATIC_CONTAINER': None,
    'FILTER_LIST': [],
    'HEADERS': {},
    'GZIP_CONTENT_TYPES': [],
}

if hasattr(settings, 'CUMULUS'):
    CUMULUS.update(settings.CUMULUS)

# set auth_url to the actual URL string in the cloudfiles module
CUMULUS['AUTH_URL'] = getattr(cloudfiles, CUMULUS['AUTH_URL'])

# backwards compatibility for old-style cumulus settings
if not hasattr(settings, 'CUMULUS') and hasattr(settings, 'CUMULUS_API_KEY'):
    import warnings
    warnings.warn(
        "settings.CUMULUS_* is deprecated; use settings.CUMULUS instead.",
        PendingDeprecationWarning
    )

    CUMULUS.update({
        'API_KEY': getattr(settings, 'CUMULUS_API_KEY'),
        'CNAMES': getattr(settings, 'CUMULUS_CNAMES', None),
        'CONTAINER': getattr(settings, 'CUMULUS_CONTAINER'),
        'SERVICENET': getattr(settings, 'CUMULUS_USE_SERVICENET', False),
        'TIMEOUT': getattr(settings, 'CUMULUS_TIMEOUT', 5),
        'TTL': getattr(settings, 'CUMULUS_TTL', default_cdn_ttl),
        'USERNAME': getattr(settings, 'CUMULUS_USERNAME'),
    })
