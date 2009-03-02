try:
    import simplejson
except ImportError:
    from django.utils import simplejson
import urllib, urlparse
import fetchers

class APIKeyError(Exception):
    def __init__(self, api_key, e):
        self.api_key = api_key
        self.wrapped_exception = e
    
    def __repr__(self):
        return '<APIKeyError: %s is a bad API key>' % self.api_key

class Client(object):
    base_url = 'http://api.guardianapis.com/'
    
    def __init__(self, api_key, fetcher=None):
        self.api_key = api_key
        self.fetcher = fetcher or fetchers.best_fetcher()
    
    def _do_call(self, endpoint, **kwargs):
        url = '%s?%s' % (
            urlparse.urljoin(self.base_url, endpoint),
            urllib.urlencode(self.fix_kwargs(kwargs), doseq=True)
        )
        try:
            headers, response = self.fetcher.get(url)
        except fetchers.HTTPError, e:
            if e.code == 403:
                raise APIKeyError(self.api_key, e)
            else:
                raise
        return simplejson.loads(response)
    
    def fix_kwargs(self, kwargs):
        kwargs2 = dict(kwargs)
        kwargs2['format'] = 'json'
        kwargs2['api_key'] = self.api_key
        return kwargs2
    
    def search(self, **kwargs):
        json = self._do_call('/content/search', **kwargs)
        return SearchResults(self, kwargs, json)
    
    def tags(self, **kwargs):
        json = self._do_call('/content/all-subjects', **kwargs)
        return TagResults(self, kwargs, json)
    
    def content(self, content_id):
        json = self._do_call('/content/content/%s' % content_id)
        return json
    
class Results(object):
    def __init__(self, client, kwargs, json):
        self.client = client
        self.kwargs = kwargs
        self.json = json
    
    def all(self, sleep=1):
        return AllResults(self, sleep)
    
    def __getitem__(self, key):
        return self.json[key]
    
    def results(self):
        return []
    
    def __iter__(self):
        for result in self.results():
            yield result


class SearchResults(Results):
    
    def results(self):
        return self.json['search']['results']
    
    def filters(self):
        return self.json['search']['filters']

class TagResults(Results):
    
    def results(self):
        return self.json['com.gu.gdn.api.model.TagList']['tags']


class AllResults(object):
    "Results wrapper that knows how to auto-paginate a result set"
    def __init__(self, results, sleep=1):
        self.results = results
        self.client = results.client
        self.sleep = sleep

    def __iter__(self):
        # TODO: Implement this method properly
        current_index = 0
        total_fetched = 0
        
        results = self.results
        kwargs = dict(results.kwargs)
        
        for result in results:
            yield result
