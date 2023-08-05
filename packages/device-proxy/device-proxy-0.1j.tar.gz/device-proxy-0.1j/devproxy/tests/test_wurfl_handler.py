import hashlib

from twisted.internet.defer import inlineCallbacks

from devproxy.handlers.wurfl_handler.simple import SimpleWurflHandler
from devproxy.utils import http
from devproxy.tests.utils import FakeMemcached, ProxyTestCase


class WurlfHandlerTestCase(ProxyTestCase):

    @inlineCallbacks
    def setUp(self):
        yield super(WurlfHandlerTestCase, self).setUp()
        self.fake_memcached = FakeMemcached()
        self.patch(SimpleWurflHandler, 'connect_to_memcached',
            self.patch_memcached)

        self.wurfl_handlers = yield self.start_handlers([SimpleWurflHandler({
            'header_name': 'X-UA-header',
            'cache_prefix': 'prefix',
            'cache_prefix_delimiter': '_',
            'cache_lifetime': 100,
            'debug_path': '/_debug',
        })])

    def patch_memcached(self, **config):
        return self.fake_memcached

    @inlineCallbacks
    def test_wurfl_nokia_lookup(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        response = yield http.request(url, headers={
            'User-Agent': self.nokia_ua,
            })
        self.assertEqual(response.delivered_body, 'foo')
        req = yield self.mocked_backend.queue.get()
        self.assertEqual(req.requestHeaders.getRawHeaders('x-ua-header'),
            ['medium'])

    @inlineCallbacks
    def test_wurfl_iphone_lookup(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        response = yield http.request(url, headers={
            'User-Agent': self.iphone_ua,
            })
        self.assertEqual(response.delivered_body, 'foo')
        req = yield self.mocked_backend.queue.get()
        self.assertEqual(req.requestHeaders.getRawHeaders('x-ua-header'),
            ['high'])

    @inlineCallbacks
    def test_caching_prefix(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        [handler] = self.wurfl_handlers
        cache_key = handler.get_cache_key(self.iphone_ua)
        namespace_version = yield handler.get_namespace_version()
        self.assertEqual(cache_key,
            'prefix_%s_%s' % (
                namespace_version,
                hashlib.md5(self.iphone_ua).hexdigest()
            )
        )

    @inlineCallbacks
    def test_cache_clearing(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        [handler] = self.wurfl_handlers
        namespace_version = yield handler.get_namespace_version()
        self.assertEqual(namespace_version, '0')
        yield handler.increment_namespace()
        namespace_version = yield handler.get_namespace_version()
        self.assertEqual(namespace_version, '1')

    @inlineCallbacks
    def test_caching_wurfl_check(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        [handler] = self.wurfl_handlers
        yield http.request(url, headers={
            'User-Agent': self.iphone_ua,
            })
        cache_key = handler.get_cache_key(self.iphone_ua)
        self.assertTrue(cache_key in self.fake_memcached)

        response = yield http.request(url, headers={
            'User-Agent': self.iphone_ua,
            })

        self.assertEqual(response.delivered_body, 'foo')
        self.assertEqual(self.fake_memcached.times_called(cache_key), 1)
        self.assertTrue(self.fake_memcached.get(cache_key))
        req = yield self.mocked_backend.queue.get()
        self.assertEqual(req.requestHeaders.getRawHeaders('X-UA-header'),
            ['high'])

    @inlineCallbacks
    def test_cache_lifetime(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        [handler] = self.wurfl_handlers
        request_path = "/some/random/path?true=1"
        response = yield http.request('%s%s' % (url, request_path),
            headers={
                'User-Agent': self.iphone_ua,
            })
        self.assertEqual(response.delivered_body, 'foo')
        cache_key = handler.get_cache_key(self.iphone_ua)
        self.assertEqual(self.fake_memcached.key_lifetime(cache_key), 100)

    @inlineCallbacks
    def test_debug_path(self):
        proxy, url = self.start_proxy(self.wurfl_handlers)
        request_path = "/_debug"
        response = yield http.request('%s%s' % (url, request_path),
            headers={
                'User-Agent': self.iphone_ua,
            }, method='GET')
        self.assertEqual(response.code, 200)
