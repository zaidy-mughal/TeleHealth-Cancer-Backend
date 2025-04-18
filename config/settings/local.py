import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("POSTGRES_DB", "telehealth_db"),
        'USER': os.getenv("POSTGRES_USER", "telehealth_user"),
        'PASSWORD': os.getenv("POSTGRES_PASSWORD", "telehealth_pass"),
        'HOST': os.getenv("POSTGRES_HOST", "db"),
        'PORT': os.getenv("POSTGRES_PORT", "5432"),
    }
}
