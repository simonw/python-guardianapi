import urllib2

def best_fetcher():
    try:
        import httplib2
        return CachedFetcher()
    except ImportError:
        return Fetcher()

class HTTPError(Exception):
    def __init__(self, status_code, info=None):
        self.status_code = status_code
        self.info = info

class Fetcher(object):
    "Default implementation, using urllib2"
    def get(self, url):
        try:
            u = urllib2.urlopen(url)
        except urllib2.HTTPError, e:
            raise HTTPError(e.code, e)
        headers = u.headers.dict
        return headers, u.read()

class CachedFetcher(object):
    "Requires httplib2"
    def __init__(self, cache=None):
        import httplib2
        if cache is None:
            cache = CachedFetcher._Cache()
        self.http = httplib2.Http(cache)
    
    def get(self, url):
        headers, response = self.http.request(url)
        if headers['status'] != '200':
            raise HTTPError(int(headers['status']), headers)
        return headers, response
    
    class _Cache(object):
        def __init__(self):
            self._cache = {}
        
        def get(self, key):
            return self._cache.get(key)
        
        def set(self, key, value):
            self._cache[key] = value
        
        def delete(key):
            if key in self._cache[key]:
                del self._cache[key]
