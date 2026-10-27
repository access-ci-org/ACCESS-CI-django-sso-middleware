# ACCESS-CI-django-sso-middleware

Django middleware that keeps the local session in step with the shared ACCESS SSO cookie (`SESSaccesscisso`).

- Authenticated and cookie present: request passes through.
- Cookie present but no local session: redirect to `settings.LOGIN_URL?next=<path>` (skipped inside the CILogon login flow).
- Authenticated but cookie missing: the cookie is set on the response.
- Still logged out after the view with the cookie present: the stale `sso_token` cookie is deleted.

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

It must come after `AuthenticationMiddleware`. It uses `LOGIN_URL`, `SESSION_COOKIE_AGE` and `SESSION_COOKIE_DOMAIN`.

## Optional settings

| Setting | Default |
|---|---|
| `ACCESS_CI_SSO_SSO_COOKIE_NAME` | `SESSaccesscisso` |
| `ACCESS_CI_SSO_STALE_TOKEN_COOKIE_NAME` | `sso_token` |
| `ACCESS_CI_SSO_LOGIN_FLOW_PATHS` | `/accounts/cilogon/login/`, `/accounts/cilogon/login/callback/` |

## Tests

    python -m unittest tests.test_middleware
