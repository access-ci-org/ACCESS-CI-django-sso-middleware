import logging

from django.conf import settings
from django.shortcuts import redirect

from .conf import get_setting

logger = logging.getLogger(__name__)


class ACCESSCISSOMiddleware:
    """Keep the local Django session in step with the shared ACCESS SSO cookie.

    Must be placed after AuthenticationMiddleware in MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.sso_cookie_name = get_setting("SSO_COOKIE_NAME")
        self.stale_token_cookie_name = get_setting("STALE_TOKEN_COOKIE_NAME")
        self.login_flow_paths = frozenset(get_setting("LOGIN_FLOW_PATHS"))

    def __call__(self, request):
        sso_cookie = request.COOKIES.get(self.sso_cookie_name)
        is_authenticated = request.user.is_authenticated
        logger.debug(
            "path=%s sso_cookie=%s authenticated=%s",
            request.path, sso_cookie, is_authenticated,
        )

        # Authenticated with the SSO cookie present: nothing to do.
        if is_authenticated and sso_cookie:
            return self.get_response(request)

        # SSO cookie but no local session: send them to log in, unless they
        # are already in the login flow.
        if sso_cookie and not is_authenticated and request.path not in self.login_flow_paths:
            return redirect(f"{settings.LOGIN_URL}?next={request.path}")

        response = self.get_response(request)

        # Logged in without the SSO cookie (e.g. just logged in): set it.
        if request.user.is_authenticated and not sso_cookie:
            response.set_cookie(
                self.sso_cookie_name,
                value="1",
                max_age=settings.SESSION_COOKIE_AGE,
                domain=settings.SESSION_COOKIE_DOMAIN,
                samesite="Lax",
            )

        # Still logged out after the view: drop the stale token cookie.
        if sso_cookie and not request.user.is_authenticated:
            response.delete_cookie(
                self.stale_token_cookie_name,
                domain=settings.SESSION_COOKIE_DOMAIN,
                path="/",
            )

        return response
