"""
A Python client for the WordPress JSON API
"""
# This library is aimed at easier communication between
# Python-based projects and a wordpress installation.

__author__ = "Chris Amico (eyeseast@gmail.com)"
__version__ = "0.1.2"
__license__ = "MIT"

import httplib2
import os
import urllib
import urlparse
try:
    import json
except ImportError:
    import simplejson as json

__all__ = ('WordPress', 'WordPressError')

# Setting debug to True will add requested URLs to returned JSON
DEBUG = False

DEFAULT_METHODS = [
    'info',
    'get_recent_posts',
    'get_post',
    'get_page',
    'get_date_posts',
    'get_category_posts',
    'get_tag_posts',
    'get_author_posts',
    'get_search_results',
    'get_date_index',
    'get_category_index',
    'get_tag_index',
    'get_author_index',
    'get_page_index',
    # 'get_nonce'
]

class WordPressError(Exception):
    """
    An error for things that break with WordPress
    """

# ## WordPress
# Create an instance with a blog's URL, and cache setting. WordPress uses 
# [httplib2](http://code.google.com/p/httplib2/) under the hood, and caching
# is pluggable. It's possible to pass in a `django.core.cache.cache` object
# here to use the same cache backend you've set up for a Django project.
# 
# See [httplib2 docs](http://httplib2.googlecode.com/hg/doc/html/libhttplib2.html#id1)
# for more on cache backends.
class WordPress(object):
    """
    The main wrapper
    """
    def __init__(self, blog_url, cache='.cache'):
        self.dev = 0
        self.blog_url = blog_url
        if not self.blog_url.endswith('?'):
            self.blog_url += "?"
        self._http = httplib2.Http(cache)
    
    def __repr__(self):
        return "<WordPress: %s>" % self.blog_url.rstrip('?')
    
    # method does most of the dirty work. Pass in an API method and
    # some kwargs and it grabs, parses and returns some useful JSON
    def method(self, method_name, **kwargs):
        """
        Build a URL for this method + kwargs, then fetch it.
        """
        kwargs.setdefault('dev', self.dev)
        kwargs['json'] = method_name
        url = self.blog_url + urllib.urlencode(kwargs)

        return self.fetch(url)
    
    def fetch(self, url):
        "Grab, parse and return the actual response"
        r, c = self._http.request(url)
        c = json.loads(c)
        if c.get('status', '').lower() == "error" or "error" in c:
            raise WordPressError(c.get('error'))
        
        if DEBUG:
            c['_url'] = url
        return c

    def proxy(self, path):
        """
        Get the JSON version of the given path, joined with self.blog_url
        """
        url = urlparse.urljoin(self.blog_url, path) + '?'
        url += urllib.urlencode({'json': 1})

        return self.fetch(url)
        
    # The WordPress JSON API is really simple. Give it a named method
    # in a query string--`?json=get_recent_posts`--and it returns JSON. 
    # Since all we're doing is passing methods and arguments, there's
    # little point re-defining those methods in Python
    def __getattr__(self, method_name):
        """
        Return a callable API method if `method` is in self._methods
        """
        if method_name in DEFAULT_METHODS:
            def _api_method(**kwargs):
                return self.method(method_name, **kwargs)
            _api_method.__name__ = method_name
            return _api_method
        else:
            raise AttributeError
