import os

from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# Основные настройки
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1').split(',')
SITE_DOMAIN = os.getenv('SITE_DOMAIN', '127.0.0.1:8000')

# Application definition
INSTALLED_APPS = [
    # Стандартные приложения Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django_apscheduler',

    # Приложения allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.yandex',

    # Мои приложения
    'news.apps.NewsConfig',
    'accounts',
    'django_filters',
    'sign',
    'protect',
    'appointment.apps.AppointmentConfig',
]

# Настройки сайта
SITE_ID = int(os.getenv('SITE_ID', '1'))

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'Newsportal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Необходим для allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    # Необходим для входа в админку Django
    'django.contrib.auth.backends.ModelBackend',
    # Специфичные методы аутентификации allauth
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'Newsportal.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / os.getenv('DATABASE_NAME', 'db.sqlite3'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Настройки аутентификации
LOGIN_URL = '/accounts/login/'  # Используем URL от allauth
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Настройки allauth
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_VERIFICATION = os.getenv('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
ACCOUNT_FORMS = {'signup': 'sign.models.BasicSignupForm'}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'yandex': {
        'SCOPE': ['login:email', 'login:info'],
    }
}

# Настройки почты
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '465'))
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'True') == 'True'
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
SERVER_EMAIL = os.getenv('SERVER_EMAIL')

ADMINS = [
    ('Irina', 'irinaosk206@gmail.com'),
    # список всех админов в формате ('имя', 'их почта')
]

MANAGERS = [
    ('Irina', 'irinaosk206@gmail.com'),
]

# Настройки APScheduler
APSCHEDULER_DATETIME_FORMAT = os.getenv('APSCHEDULER_DATETIME_FORMAT', 'N j, Y, f:s a')
APSCHEDULER_RUN_NOW_TIMEOUT = int(os.getenv('APSCHEDULER_RUN_NOW_TIMEOUT', '25'))

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'cache_files'),
        'TIMEOUT': 300,  #по умолчанию 5 минут
    }
}

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'style': '{',

    'formatters': {
        'debug_console': {
            'format': '{asctime} - {levelname} - {message}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
        'warning_console': {
            'format': '{asctime} - {levelname} - {pathname} - {message}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
        'error_console': {
            'format': '{asctime} - {levelname} - {pathname} - {message}\n{exc_info}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
        'file_general': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
        'file_errors': {
            'format': '{asctime} - {levelname} - {message} - {pathname}\n{exc_info}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
        'file_security': {
            'format': '{asctime} - {levelname} - {module} - {message}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
        'mail': {
            'format': '{asctime} - {levelname} - {message} - {pathname}',
            'style': '{',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
    },

    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },

    'handlers': {
        # DEBUG/INFO (только при DEBUG=True)
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'debug_console',
        },
        # только при DEBUG=True
        'console_warning': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'warning_console',
        },
        # только при DEBUG=True
        'console_error': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'error_console',
        },

        # только при DEBUG=False
        'file_general': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'general.log',
            'filters': ['require_debug_false'],
            'formatter': 'file_general',
        },

        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'errors.log',
            'formatter': 'file_errors',
        },

        'file_security': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'formatter': 'file_security',
        },

        # только при DEBUG=False
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'mail',
        },
    },

    'loggers': {
        'django': {
            'handlers': [
                'console_debug',
                'console_warning',
                'console_error',
                'file_general',
            ],
            'level': 'DEBUG',
            'propagate': True,
        },

        # Ошибки запросов и сервера
        'django.request': {
            'handlers': ['file_errors', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['file_errors', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },

        # Шаблоны и база
        'django.template': {
            'handlers': ['file_errors'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['file_errors'],
            'level': 'ERROR',
            'propagate': False,
        },

        # Безопасность
        'django.security': {
            'handlers': ['file_security'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}