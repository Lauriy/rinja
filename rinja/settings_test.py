from rinja.settings import *

assert ROOT_URLCONF

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

SECRET_KEY = 'moxqms%4zujsgd!c*y#36d!7#dh2e)+of-zla+)z9m09e)cvb%'

GOOGLE_APPLICATION_CREDENTIALS = ''
