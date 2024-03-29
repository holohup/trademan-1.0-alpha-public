import os

from dotenv import load_dotenv
from tinkoff.invest.retrying.settings import RetryClientSettings

DEBUG_DB = False
load_dotenv()
TCS_RW_TOKEN = os.getenv('TCS_RW_TOKEN', '000')
TCS_ACCOUNT_ID = os.getenv('ACCOUNT_ID', '000')
TCS_RO_TOKEN = os.getenv('TCS_RO_TOKEN', '000')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'se))@dqt_6p=esf*x=@o6$7#28=pv7g-2tjtul_z2m*1ayxfn%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.2.40', '127.0.0.1', 'localhost', '192.168.2.179', '192.168.2.180', '192.168.2.100', 'prod']

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': True,
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'base',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'trademan.daily_updater.daily_updater'
]

ROOT_URLCONF = 'trademan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'trademan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

if DEBUG_DB:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'formatter': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(name)s %(asctime)s %(filename)s: %(lineno)d - %(funcName)s()] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'formatter',
            },
        },
        'loggers': {
            'django': {
                'handlers': ('console',),
                'level': 'INFO',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ('console',),
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    }

RETRY_SETTINGS = RetryClientSettings(use_retry=True, max_retry_attempt=100)
