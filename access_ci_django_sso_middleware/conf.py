from django.conf import settings

DEFAULTS = {
    "SSO_COOKIE_NAME": "SESSaccesscisso",
    "STALE_TOKEN_COOKIE_NAME": "sso_token",
    "LOGIN_FLOW_PATHS": (
        "/accounts/cilogon/login/",
        "/accounts/cilogon/login/callback/",
    ),
}


def get_setting(name):
    """Read ACCESS_CI_SSO_<name> from Django settings, falling back to the default."""
    return getattr(settings, f"ACCESS_CI_SSO_{name}", DEFAULTS[name])
