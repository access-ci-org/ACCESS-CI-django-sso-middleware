from django.conf import settings

settings.configure(
    SECRET_KEY="x",
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"],
    LOGIN_URL="/login/",
    ROOT_URLCONF="tests.urls",
    SESSION_COOKIE_AGE=100,
    SESSION_COOKIE_DOMAIN=".access-ci.org",
)

import django  # noqa: E402

django.setup()

from django.contrib.auth.models import AnonymousUser  # noqa: E402
from django.http import HttpResponse  # noqa: E402
from django.test import RequestFactory, SimpleTestCase  # noqa: E402

from access_ci_django_sso_middleware.middleware import ACCESSCISSOMiddleware  # noqa: E402


class User:
    is_authenticated = True


def run(path="/", cookie=None, user=None):
    request = RequestFactory().get(path)
    if cookie:
        request.COOKIES["SESSaccesscisso"] = cookie
    request.user = user or AnonymousUser()
    return ACCESSCISSOMiddleware(lambda r: HttpResponse("ok"))(request)


class MiddlewareTests(SimpleTestCase):
    def test_authenticated_with_cookie_passes_through(self):
        r = run(cookie="1", user=User())
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("SESSaccesscisso", r.cookies)

    def test_cookie_without_session_redirects(self):
        r = run("/x/", cookie="1")
        self.assertEqual((r.status_code, r["Location"]), (302, "/login/?next=/x/"))

    def test_login_flow_path_not_redirected_and_stale_cookie_cleared(self):
        r = run("/accounts/cilogon/login/", cookie="1")
        self.assertEqual(r.status_code, 200)
        self.assertIn("sso_token", r.cookies)

    def test_authenticated_without_cookie_sets_cookie(self):
        r = run(user=User())
        self.assertEqual(r.cookies["SESSaccesscisso"].value, "1")

    def test_anonymous_without_cookie_untouched(self):
        r = run()
        self.assertEqual(len(r.cookies), 0)
