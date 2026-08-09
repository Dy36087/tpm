from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

try:
    import whitenoise

    WHITENOISE_INSTALLED = True
except ImportError:
    WHITENOISE_INSTALLED = False

# Carregar variáveis de .env se existir
if load_dotenv:
    load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-*hlj6ov+d+6u9h2y*(gk^jz^cput0px27ub9mc_o+am$+s-gjn",
)

# SECURITY WARNING: don't run with debug turned on in production!
# Set `DJANGO_DEBUG` env var to 'False' in production.
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

# Hosts
DEFAULT_ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".herokuapp.com"]
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = DEFAULT_ALLOWED_HOSTS

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_TRUSTED_ORIGINS = [
        origin.strip()
        for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
        if origin.strip()
    ]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cadptm.apps.CadptmConfig",
    "principal.apps.PrincipalConfig",
    "pontoele.apps.PontoeleConfig",
    "cadferramentas.apps.CadferramentasConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Inserir WhiteNoise no middleware quando disponível (apenas para produção)
if WHITENOISE_INSTALLED:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "ptm.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ptm.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Usar DATABASE_URL em produção (Postgres), SQLite em desenvolvimento
if "DATABASE_URL" in os.environ:
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"), conn_max_age=600
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "pt-br"

TIME_ZONE = "America/Sao_Paulo"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "templates/static"),
    os.path.join(BASE_DIR, "static"),
)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Use WhiteNoise to serve static files in production when installed
if WHITENOISE_INSTALLED:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Autenticação: URLs de redirecionamento padrão
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/patrimonio/"
LOGOUT_REDIRECT_URL = "/login/"
