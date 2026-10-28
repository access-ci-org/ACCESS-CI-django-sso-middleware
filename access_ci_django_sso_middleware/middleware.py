import logging
from urllib.parse import urlencode

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
        self.sso_cookie_domain = get_setting("SSO_COOKIE_DOMAIN")
        self.cilogon_login_url = get_setting("CILOGON_LOGIN_URL")
        self.cilogon_logout_url = get_setting("CILOGON_LOGOUT_URL")
        self.login_flow_paths = frozenset(get_setting("LOGIN_FLOW_PATHS"))

    def __call__(self, request):
        sso_cookie = request.COOKIES.get(self.sso_cookie_name)
        is_authenticated = request.user.is_authenticated
        logger.debug(
            "path=%s sso_cookie=%s authenticated=%s",
            request.path, sso_cookie, is_authenticated,
        )

        # SSO cookie but no local session: start the CILogon OAuth login
        # (allauth provider login view), unless they are already in the
        # login flow.
        if sso_cookie and not is_authenticated and request.path not in self.login_flow_paths:
            query = urlencode({"process": "login", "next": request.get_full_path()})
            return redirect(f"{self.cilogon_login_url}?{query}")

        response = self.get_response(request)
        is_authenticated_now = request.user.is_authenticated

        if is_authenticated and not is_authenticated_now:
            # The view logged the user out: remove the SSO cookie too.
            if not request.path.startswith(settings.LOGIN_URL):
                response = redirect(self.cilogon_logout_url)
            response.delete_cookie(
                self.sso_cookie_name,
                domain=self.sso_cookie_domain,
                path="/",
                samesite="Lax",
            )
        elif is_authenticated_now and not sso_cookie:
            # Logged in without the SSO cookie (e.g. just logged in): set it.
            response.set_cookie(
                self.sso_cookie_name,
                value="1",
                max_age=settings.SESSION_COOKIE_AGE,
                domain=self.sso_cookie_domain,
                samesite="Lax",
            )
        elif sso_cookie and not is_authenticated_now:
            # Still logged out after the view: end the CILogon session too,
            # except inside the login flow itself, where this would cancel
            # the login redirect. Either way, drop the SSO cookie.
            if not request.path.startswith(settings.LOGIN_URL):
                response = redirect(self.cilogon_logout_url)
            response.delete_cookie(
                self.sso_cookie_name,
                domain=self.sso_cookie_domain,
                path="/",
                samesite="Lax",
            )

        return response
