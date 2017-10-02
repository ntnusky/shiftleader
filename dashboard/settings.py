"""
Django settings for dashboard project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from configparser import ConfigParser,NoOptionError


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

parser = ConfigParser()
parser.read(['/etc/machineadmin/settings.ini', os.path.join(BASE_DIR, 'settings.ini')])

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'z^&g=*k^qw&-hr%tlv#=0u+(ij910&!ld)__*4i#gq$*!4==6@'
SECRET_KEY = parser.get('general', 'secret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = parser.getboolean('general', 'debug') 

ALLOWED_HOSTS = []
hosts = parser.items("hosts")
for key, host in hosts:
  ALLOWED_HOSTS.append(host)


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_python3_ldap',
    'dashboard',
    'puppet',
    'dhcp',
    'nameserver',
    'host',
)

AUTHENTICATION_BACKENDS = ("django_python3_ldap.auth.LDAPBackend",)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'dashboard.urls'

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

WSGI_APPLICATION = 'dashboard.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

dbtype = parser.get('database', 'type')
if(dbtype == 'mysql'):
  DATABASES['default']['ENGINE'] = 'django.db.backends.mysql'                    
  DATABASES['default']['HOST'] = parser.get('database', 'host')                  
  DATABASES['default']['NAME'] = parser.get('database', 'name')                  
  DATABASES['default']['USER'] = parser.get('database', 'user')                  
  DATABASES['default']['PASSWORD'] = parser.get('database', 'password')
else:                                                                            
  dbtype = 'sqlite'                                                              
  try:                                                                           
    n = parser.get('database', 'name')                                           
  except NoOptionError:                                             
    n = 'db.sqlite3'                                                             
                                                                                 
  if(n[0] == '/'):                                                               
    name = n                                                                     
  else:                                                                          
    name = os.path.join(BASE_DIR, n)                                             
                                                                                 
  DATABASES['default']['ENGINE'] = 'django.db.backends.sqlite3'                  
  DATABASES['default']['NAME'] = name


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
try:
  STATIC_ROOT = parser.get('general', 'staticpath')
except NoOptionError:
  STATIV_ROOT = None
LOGIN_URL = '/login/'

# The URL of the LDAP server.
LDAP_AUTH_URL = parser.get('LDAP', 'url') 

# Initiate TLS on connection.
LDAP_AUTH_USE_TLS = False

# The LDAP search base for looking up users.
LDAP_AUTH_SEARCH_BASE = parser.get('LDAP', 'search-base')

# The LDAP class that represents a user.
LDAP_AUTH_OBJECT_CLASS = "user"

# User model fields mapped to the LDAP
# attributes that represent them.
LDAP_AUTH_USER_FIELDS = {
    "username": "sAMAccountName",
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}

# A tuple of django model fields used to uniquely identify a user.
LDAP_AUTH_USER_LOOKUP_FIELDS = ("username",)

# Path to a callable that takes a dict of {model_field_name: value},
# returning a dict of clean model data.
# Use this to customize how data loaded from LDAP is saved to the User model.
LDAP_AUTH_CLEAN_USER_DATA = "django_python3_ldap.utils.clean_user_data"

# Path to a callable that takes a user model and a dict of {ldap_field_name: [value]},
# and saves any additional user relationships based on the LDAP data.
# Use this to customize how data loaded from LDAP is saved to User model relations.
# For customizing non-related User model fields, use LDAP_AUTH_CLEAN_USER_DATA.
LDAP_AUTH_SYNC_USER_RELATIONS = "django_python3_ldap.utils.sync_user_relations"

# Path to a callable that takes a dict of {ldap_field_name: value},
# returning a list of [ldap_search_filter]. The search filters will then be AND'd
# together when creating the final search filter.
LDAP_AUTH_FORMAT_SEARCH_FILTERS = "django_python3_ldap.utils.format_search_filters"

# Path to a callable that takes a dict of {model_field_name: value}, and returns
# a string of the username to bind to the LDAP server.
# Use this to support different types of LDAP server.
#LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_openldap"

#LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory"

#LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory_principal"
#LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = "win.ntnu.no"

LDAP_AUTH_FORMAT_USERNAME = "django_python3_ldap.utils.format_username_active_directory"
LDAP_AUTH_ACTIVE_DIRECTORY_DOMAIN = parser.get('LDAP', 'domain')

# The LDAP username and password of a user for querying the LDAP database for user
# details. If None, then the authenticated user will be used for querying, and
# the `ldap_sync_users` command will perform an anonymous query.
LDAP_AUTH_CONNECTION_USERNAME = None
LDAP_AUTH_CONNECTION_PASSWORD = None
