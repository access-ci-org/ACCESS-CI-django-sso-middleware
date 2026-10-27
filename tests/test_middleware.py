from django.conf import settings

settings.configure(
    SECRET_KEY="x",
    INSTALLED_APPS=["django.contrib.auth", "django.contrib.contenttypes"],
    LOGIN_URL="/accounts/cilogon/login/",
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
    def __init__(self):
        self.is_authenticated = True


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
        self.assertEqual((r.status_code, r["Location"]), (302, "/accounts/cilogon/login/?next=/x/"))

    def test_login_flow_path_not_redirected_and_sso_cookie_cleared(self):
        r = run("/accounts/cilogon/login/", cookie="1")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.cookies["SESSaccesscisso"].value, "")

    def test_still_logged_out_redirects_to_cilogon_logout(self):
        r = run("/accounts/logout/", cookie="1")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r["Location"], "https://cilogon.org/logout/?skin=access")
        self.assertEqual(r.cookies["SESSaccesscisso"].value, "")

    def test_authenticated_without_cookie_sets_cookie(self):
        r = run(user=User())
        self.assertEqual(r.cookies["SESSaccesscisso"].value, "1")

    def test_logout_deletes_sso_cookie(self):
        user = User()

        def view(request):
            user.is_authenticated = False  # simulates auth.logout() in the view
            return HttpResponse("bye")

        request = RequestFactory().get("/accounts/logout/")
        request.COOKIES["SESSaccesscisso"] = "1"
        request.user = user
        r = ACCESSCISSOMiddleware(view)(request)
        morsel = r.cookies["SESSaccesscisso"]
        self.assertEqual(morsel.value, "")
        self.assertEqual(morsel["max-age"], 0)
        self.assertEqual(morsel["domain"], ".access-ci.org")

    def test_anonymous_without_cookie_untouched(self):
        r = run()
        self.assertEqual(len(r.cookies), 0)
