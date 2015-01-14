""" Responsible for interacting directly with the Raven service. """

import cookielib
import mechanize
from error import RavenAuthenticationError

RAVEN_URL = 'https://raven.cam.ac.uk/auth/login.html'
_DEFAULT_AUTHENTICATED_BROWSER = None
_CACHED_BROWSERS = {}


def set_default_credentials(crsid, password):
    """ Specify the Raven credentials to use for tasks not related to any
    specific user.
    :raises: RavenAuthenticationError if crsid/password isn't accepted by Raven
    """
    global _DEFAULT_AUTHENTICATED_BROWSER
    browser = get_authenticated_browser(crsid, password)
    _DEFAULT_AUTHENTICATED_BROWSER = browser


def get_default_authenticated_browser():
    """ Get the Raven authenticated mechanize browser not associated with any
    specific user.
    :return: mechanize.Browser() instance authenticated with Raven using the
        previously specified default credentials
    :raises: RavenAuthenticationError if no valid default credentials have been
        specified previously using `set_default_credentials()`
    """
    global _DEFAULT_AUTHENTICATED_BROWSER
    if _DEFAULT_AUTHENTICATED_BROWSER is None:
        error_message = 'No default credentials supplied to raven_service'
        raise RavenAuthenticationError(error_message)
    return _DEFAULT_AUTHENTICATED_BROWSER


def get_authenticated_browser(crsid, password):
    """ Get a mechanize browser, authenticated against Raven using the supplied
    credentials.
    :return: mechanize.Browser() instance authenticated with Raven using
        `crsid` and `password`
    :raises: RavenAuthenticationError if crsid/password isn't accepted by Raven
    """
    if crsid not in _CACHED_BROWSERS:
        cookie_jar = cookielib.LWPCookieJar()
        browser = mechanize.Browser()
        browser.set_cookiejar(cookie_jar)
        browser.set_handle_equiv(True)
        browser.set_handle_redirect(True)
        browser.set_handle_referer(True)
        browser.set_handle_robots(False)
        browser.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(),
                                   max_time=1)

        browser.addheaders = [('User-agent',
                               'Mozilla/5.0 '
                               '(X11; U; Linux i686; en-US; rv:1.9.0.1) '
                               'Gecko/2008071615 Fedora/3.0.1-1.fc9 '
                               'Firefox/3.0.1')]

        browser.open(RAVEN_URL)
        browser.select_form(nr=0)
        browser.form['userid'] = crsid
        browser.form['pwd'] = password
        browser.submit()

        if len(cookie_jar) == 0:
            error_message = 'Incorrect crsid/password combination'
            raise RavenAuthenticationError(error_message)
        else:
            _CACHED_BROWSERS[crsid] = browser
    return _CACHED_BROWSERS[crsid]