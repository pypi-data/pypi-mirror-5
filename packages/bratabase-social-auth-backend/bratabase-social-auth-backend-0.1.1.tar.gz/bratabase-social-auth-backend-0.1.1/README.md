Bratabase social-auth Backend
=============================

OAuth2 Backend for Bratabase.com to be used with Django-social-auth.

    https://github.com/omab/django-social-auth

# Installation

```
$ pip install bratabase-social-auth-backend
```

To enable, simply add the following to your `settings.py`:

```
AUTHENTICATION_BACKENDS = [
    ... your other backends
    'bratabase_social_auth.backends.bratabase.BratabaseBackend',
    'django.contrib.auth.backends.ModelBackend',
]

```

And add a **Connect with Bratabase** button that points to `{% url 'socialauth_begin' 'bratabase' %}`.



