# -*- coding: utf-8 -*-

"""Enforce HTTP Strict Transport Security (see e.g.: `#`_).
  
  _`#`: http://www.imperialviolet.org/2012/07/19/hope9talk.html
"""

import logging
logger = logging.getLogger(__name__)

import urlparse

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.request import Request
from pyramid.settings import asbool

def ensure_secure_url(url, parse_url=None):
    """Add an ``s`` to the ``url`` protocol, if necessary."""
    
    if parse_url is None:
        parse_url = urlparse.urlparse
    
    # If it's not secure, append an ``s`` to the protocol.
    parsed = parse_url(url)
    protocol = parsed.scheme
    if protocol and not protocol.endswith('s'):
        original_protocol = '{0}://'.format(protocol)
        secure_protocol = '{0}s://'.format(protocol)
        url = url.replace(original_protocol, secure_protocol, 1)
    return url


def hsts_redirect_to_https(event):
    """Redirects `http://` GET requests to `https://` and blocks non `https://`
      requests to other request methods.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_event = Mock()
          >>> mock_event.request = mock_request
      
      Noop unless ``settings['hsts.force_https']`` is true::
      
          >>> mock_request.registry.settings = {}
          >>> hsts_redirect_to_https(mock_event)
          >>> mock_request.registry.settings = {'hsts.force_https': 'false'}
          >>> hsts_redirect_to_https(mock_event)
          
      Noop if the request is over https://
      
          >>> mock_request.registry.settings = {'hsts.force_https': 'true'}
          >>> mock_request.scheme = 'https'
          >>> hsts_redirect_to_https(mock_event)
      
      Or if the value of the configured ``hsts.protocol_header`` is https::
      
          >>> mock_request.scheme = 'http'
          >>> mock_request.registry.settings = {'hsts.force_https': 'true',
          ...         'hsts.protocol_header': 'Foo'}
          >>> mock_request.headers = {'Foo': 'https'}
          >>> hsts_redirect_to_https(mock_event)
      
      Otherwise if a GET request, redirects to the https equivalent::
      
          >>> mock_request.scheme = 'http'
          >>> mock_request.registry.settings = {'hsts.force_https': 'true',
          ...         'hsts.protocol_header': 'Foo'}
          >>> mock_request.headers = {'Foo': 'http'}
          >>> mock_request.method = 'GET'
          >>> mock_request.url = 'http://foo.com'
          >>> hsts_redirect_to_https(mock_event)
          Traceback (most recent call last):
          ...
          HTTPFound: The resource was found at
      
      Otherwise forbidden::
      
          >>> mock_request.method = 'POST'
          >>> hsts_redirect_to_https(mock_event)
          Traceback (most recent call last):
          ...
          HTTPForbidden: Access was denied to this resource.
      
    """
    
    # Unpack the event.
    request = event.request
    settings = request.registry.settings
    
    # Exit unless told to enforce https.
    should_force_https = asbool(settings.get('hsts.force_https', False))
    if not should_force_https:
        return
    
    # Exit if this is https (or any secure protocol).
    if request.scheme.endswith('s'):
        return
    # E.g.: on Heroku, they pass the protocol though using `X-Forwarded-Proto`.
    protocol_header = settings.get('hsts.protocol_header', None)
    if protocol_header:
        protocol = request.headers.get(protocol_header)
        if protocol and protocol.endswith('s'):
            return
    
    # If this is an insecure GET request, then redirect.
    if request.method == 'GET' or request.method == 'HEAD':
        url_parts = request.url.split('://')
        secure_location = 's://'.join(url_parts)
        raise HTTPFound(location=secure_location)
    
    # Otherwise refuse the request.
    raise HTTPForbidden()

def set_hsts_header(event):
    """Add a ``Strict-Transport-Security`` header to the response.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_request = Mock()
          >>> mock_response = Mock()
          >>> mock_event = Mock()
          >>> mock_event.request = mock_request
          >>> mock_event.response = mock_response
      
      Noop unless ``settings['hsts.force_https']`` is true::
      
          >>> mock_request.registry.settings = {}
          >>> set_hsts_header(mock_event)
          >>> mock_response.headers.add.called
          False
          >>> mock_request.registry.settings = {'hsts.force_https': 'false'}
          >>> set_hsts_header(mock_event)
          >>> mock_response.headers.add.called
          False
      
      Otherwise sets ``Strict-Transport-Security`` header::
      
          >>> mock_request.registry.settings = {'hsts.force_https': 'true'}
          >>> set_hsts_header(mock_event)
          >>> mock_response.headers.add.assert_called_with('Strict-Transport-Security',
          ...         'max-age=8640000 includeSubDomains')
          >>> mock_request.registry.settings = {'hsts.force_https': 'true', 
          ...         'hsts.max_age': 12, 'hsts.include_subdomains': 'false'}
          >>> set_hsts_header(mock_event)
          >>> mock_response.headers.add.assert_called_with('Strict-Transport-Security',
          ...         'max-age=12')
      
    """
    
    # Unpack the event.
    request = event.request
    response = event.response
    settings = request.registry.settings
    
    # If we should force https://
    should_force_https = asbool(settings.get('hsts.force_https', False))
    if should_force_https:
        # Set `Strict-Transport-Security` header to enable hsts.
        max_age = settings.get('hsts.max_age', 8640000)
        include_subdomains = asbool(settings.get('hsts.include_subdomains', True))
        value = 'max-age={0}'.format(max_age)
        if include_subdomains:
            value += ' includeSubDomains'
        response.headers.add('Strict-Transport-Security', value)

def secure_route_url(request, request_cls=None, secure_url=None):
    """Overrides ``route_url`` to make sure the protocol of the resulting
      link is secure.  This makes sure that the ``route_url`` function of
      a secure app running behind an https front end can't mistakenly
      output http links (for example).
    """
    
    # Test jig.
    if request_cls is None:
        request_cls = Request
    if secure_url is None:
        secure_url = ensure_secure_url
    
    # Cache the original ``request.route_url`` method.
    original_route_url = request_cls(request.environ).route_url
    
    def route_url(*args, **kwargs):
        """Get the original ``route_url``.  Force it to use a secure protocol."""
        
        # Get the original url.
        url = original_route_url(*args, **kwargs)
        
        # Return the secured version.
        return secure_url(url)
    
    return route_url

