from django.conf import settings

DEFAULTS = {
    "SSO_COOKIE_NAME": "SESSaccesscisso",
    "CILOGON_LOGOUT_URL": "https://cilogon.org/logout/?skin=access",
    "LOGIN_FLOW_PATHS": (
        "/accounts/cilogon/login/",
        "/accounts/cilogon/login/callback/",
        "/accounts/logout/",
    ),
}


def get_setting(name):
    """Read ACCESS_CI_SSO_<name> from Django settings, falling back to the default."""
    return getattr(settings, f"ACCESS_CI_SSO_{name}", DEFAULTS[name])
