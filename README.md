# ACCESS-CI-django-sso-middleware

Django middleware that keeps the local session in step with the shared ACCESS SSO cookie (`SESSaccesscisso`).

- Authenticated and cookie present: request passes through.
- Cookie present but no local session: redirect to `settings.LOGIN_URL?next=<path>` (skipped inside the CILogon login flow).
- A view logs the user out (e.g. `/accounts/logout/`): the SSO cookie is deleted on the response.
- Authenticated but cookie missing: the cookie is set on the response.
- Still logged out after the view with the cookie present: the SSO cookie is deleted and the user is redirected to the CILogon logout URL (not on paths under `LOGIN_URL`).

## Install

    pip install ./ACCESS-CI-django-sso-middleware

```python
INSTALLED_APPS = [..., "access_ci_django_sso_middleware"]  # optional

MIDDLEWARE = [
    ...,
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "access_ci_django_sso_middleware.middleware.ACCESSCISSOMiddleware",
]
```

It must come after `AuthenticationMiddleware`. It uses `LOGIN_URL` and `SESSION_COOKIE_AGE`.

## Optional settings

| Setting | Default |
|---|---|
| `ACCESS_CI_SSO_SSO_COOKIE_NAME` | `SESSaccesscisso` |
| `ACCESS_CI_SSO_SSO_COOKIE_DOMAIN` | `.access-ci.org` |
| `ACCESS_CI_SSO_CILOGON_LOGOUT_URL` | `https://cilogon.org/logout/?skin=access` |
| `ACCESS_CI_SSO_LOGIN_FLOW_PATHS` | `/accounts/cilogon/login/`, `/accounts/cilogon/login/callback/`, `/accounts/logout/` |

## Tests

    python -m unittest tests.test_middleware
