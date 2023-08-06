A simple app that clears user session stale cache at 4am every day

register it with :

    CELERY_IMPORTS =( 
    'celery_clearcache.tasks',
    )

in your settings.
