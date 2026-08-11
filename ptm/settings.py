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

IS_HEROKU = bool(os.environ.get("DYNO") or os.environ.get("HEROKU_APP_NAME"))
DEBUG = os.environ.get("DJANGO_DEBUG", "0" if IS_HEROKU else "1") == "1"

if IS_HEROKU:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ptm.settings")

# Hosts
DEFAULT_ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    ".herokuapp.com",
    ".app.github.dev",
]


def get_allowed_hosts():
    hosts = [
        host.strip()
        for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
        if host.strip()
    ]

    if "*" in hosts:
        return ["*"]

    if IS_HEROKU:
        return ["*"]

    hosts.extend(DEFAULT_ALLOWED_HOSTS)

    heroku_app_name = os.environ.get("HEROKU_APP_NAME")
    if heroku_app_name:
        hosts.extend([heroku_app_name, f"{heroku_app_name}.herokuapp.com"])

    runtime_host = os.environ.get("APP_DOMAIN") or os.environ.get("HOSTNAME")
    if runtime_host:
        hosts.append(runtime_host)

    return list(dict.fromkeys(hosts))


ALLOWED_HOSTS = get_allowed_hosts()
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]

if IS_HEROKU:
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = [
        "https://*.herokuapp.com",
        "https://*.app.github.dev",
        "https://*.github.dev",
        "https://*.herokuapp.com/",
    ]
else:
    ALLOWED_HOSTS = ["*"]
    CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "principal.apps.PrincipalConfig",
    "cadptm.apps.CadptmConfig",
    "cadferramentas.apps.CadferramentasConfig",
    "pontoele.apps.PontoeleConfig",
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
if "DATABASE_URL" in os.environ or os.environ.get("HEROKU_POSTGRESQL_COLOR"):
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
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "templates", "static"),
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Garantir que o ambiente online use o banco e os arquivos corretos
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if WHITENOISE_INSTALLED
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        )
    },
}

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Autenticação: URLs de redirecionamento padrão
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"
