import urllib
from urlparse import urlsplit

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from openid.consumer.consumer import Consumer, SUCCESS, CANCEL, FAILURE
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg

from .store import DjangoOpenIDStore

def get_sreg_settings():
    return getattr(settings, 'SREG_OPTIONAL', ['email', 'fullname'])

def login_begin(request, redirect_field_name=REDIRECT_FIELD_NAME,
                template_name='openid/response.html'):
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    openid_url = settings.OPENID_SSO_SERVER_URL

    if openid_url is None:
        return HttpResponseRedirect(redirect_field_name)

    consumer = make_consumer(request)
    try:
        openid_request = consumer.begin(openid_url)
    except DiscoveryFailure, exc:
        return render(
            request, template_name,
            {'message': "OpenID discovery error: %s" % str(exc)}
        )

    openid_request.addExtension(
        sreg.SRegRequest(optional=get_sreg_settings())
    )

    return_to = request.build_absolute_uri(reverse(login_complete))
    if redirect_to:
        return_to += '&' if '?' in return_to else '?'
        return_to += urllib.urlencode({redirect_field_name: redirect_to})

    return render_openid_request(request, openid_request, return_to)


def login_complete(request, redirect_field_name=REDIRECT_FIELD_NAME,
                   template_name='openid/response.html'):
    openid_response = parse_openid_response(request)
    if not openid_response:
        return render(
            request, template_name,
            {'message': 'This is an OpenID relying party endpoint.'},
            status=400
        )

    if openid_response.status == FAILURE:
        message = 'OpenID authentication failed: %s' % openid_response.message
        return render(request, template_name, {'message': message})

    if openid_response.status == CANCEL:
        return render(
            request, template_name,
            {'message': 'Authentication cancelled'},
        )

    if openid_response.status == SUCCESS:
        user = authenticate(openid_response=openid_response)
        if user is None:
            return render(
                request, template_name, {'message': 'Unkown user'}
            )
        if not user.is_active:
            return render(
                request, template_name, {'message': 'Disabled account'}
            )
        login(request, user)
        redirect_to = request.REQUEST.get(redirect_field_name, '')
        return HttpResponseRedirect(
            redirect_to=sanitise_redirect_url(redirect_to)
        )
    message = 'Unknown OpenID response type: %r' % openid_response.status
    return render(
        request, template_name, {'message': message}, status=400
    )


def sanitise_redirect_url(redirect_to):
    # Light security check -- make sure redirect_to isn't garbage.
    is_valid = True
    if not redirect_to or ' ' in redirect_to:
        is_valid = False
    elif '//' in redirect_to:
        # Allow the redirect URL to be external if it's a permitted domain
        allowed_domains = settings.ALLOWED_EXTERNAL_OPENID_REDIRECT_DOMAINS
        _, netloc, _, _, _ = urlsplit(redirect_to)
        # allow it if netloc is blank or if the domain is allowed
        if netloc:
            # a domain was specified. Is it an allowed domain?
            if netloc.find(":") != -1:
                netloc, _ = netloc.split(":", 1)
            if netloc not in allowed_domains:
                is_valid = False

    # If the return_to URL is not valid, use the default.
    if not is_valid:
        redirect_to = settings.LOGIN_REDIRECT_URL

    return redirect_to


def make_consumer(request):
    """Create an OpenID Consumer object for the given Django request."""
    session = request.session.setdefault('OPENID', {})
    store = DjangoOpenIDStore()
    return Consumer(session, store)


def render_openid_request(request, openid_request, return_to, trust_root=None):
    """Render an OpenID authentication request."""
    if trust_root is None:
        trust_root = request.build_absolute_uri('/')

    if openid_request.shouldSendRedirect():
        redirect_url = openid_request.redirectURL(trust_root, return_to)
        return HttpResponseRedirect(redirect_url)
    else:
        form_html = openid_request.htmlMarkup(
            trust_root, return_to, form_tag_attrs={'id': 'openid_message'}
        )
        return HttpResponse(form_html, content_type='text/html;charset=UTF-8')


def parse_openid_response(request):
    """Parse an OpenID response from a Django request."""
    current_url = request.build_absolute_uri()
    consumer = make_consumer(request)
    return consumer.complete(dict(request.REQUEST.items()), current_url)
