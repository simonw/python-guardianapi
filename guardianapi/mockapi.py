"""
A fetcher that returns fake replies, for running tests.
"""

from fetchers import Fetcher
import urlparse, cgi, simplejson

class MockFetcher(Fetcher):
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.fetched = [] # (url, kwargs-dict) pairs
        self.fake_total_results = 101
    
    def get(self, url):
        bits = urlparse.urlparse(url)
        endpoint = bits.path.split('/')[-1]
        args = tuple()
        if endpoint not in ('search', 'tags'):
            if bits.path.startswith('/content/item'):
                args = (endpoint,)
                endpoint = 'item'
            else:
                assert False, 'Unrecognised URL: %s' % url
        
        kwargs = cgi.parse_qs(bits.query)
        # foo=bar becomes {'foo': ['bar']} - collapse single values
        for key in kwargs:
            if isinstance(kwargs[key], list) and len(kwargs[key]) == 1:
                kwargs[key] = kwargs[key][0]
        
        method = getattr(self, 'do_%s' % endpoint)
        json = method(*args, **kwargs)
        
        self.record(url, kwargs, json)
        
        return {}, simplejson.dumps(json, indent=4)
    
    def record(self, url, args, json):
        "Record attempted URL fetches so we can run assertions against them"
        self.fetched.append((url, args))
        # print '     ', url
        # print '     ', args
        # try:
        #     print '      Got %s results' % len(json['search']['results'])
        # except KeyError:
        #     pass
    
    def do_search(self, **kwargs):
        start_index = int(kwargs.get('start-index', 0))
        count = int(kwargs.get('count', 10))
        # How many results should we return?
        num_results = min(
            self.fake_total_results - start_index, count
        )
        
        return {
            "search": {
                "count": self.fake_total_results,
                "startIndex": start_index,
                "results": [
                    self.fake_article(article_id) 
                    for article_id in range(
                        start_index, start_index + num_results
                    )
                ],
                "filters": [{
                    "name": "Article",
                    "type": "content-type",
                    "filter": "/global/article",
                    "gdnUrl": "http://mockgdnapi/content/search?filter=/global/article",
                    "webUrl": "http://www.guardian.co.uk/global/article",
                    "count": 989610,
                    "filterUrl": "http://mockgdnapi/content/search?format=json&filter=/global/article"
                } for i in range(4)]
            }
        }
    
    def do_tags(self, **kwargs):
        start_index = int(kwargs.get('start-index', 0))
        count = int(kwargs.get('count', 10))
        # How many results should we return?
        num_results = min(
            self.fake_total_results - start_index, count
        )
        
        return {
            "com.gu.gdn.api.model.TagList": {
                "count": self.fake_total_results,
                "startIndex": start_index,
                "tags": [{
                    "name": "Tag %s" % i,
                    "section": "Tags",
                    "filter": "/tag/%s" % i,
                    "gdnUrl": "http://mockgdnapi/content/search?filter=/tag/%s" % i,
                    "webUrl": "http://www.guardian.co.uk/faketag/%s" % i
                } for i in range(start_index, start_index + num_results)],
            }
        }
    
    def do_item(self, rest_of_url, **kwargs):
        return self.fake_article(rest_of_url.replace('/', ''))
    
    def fake_article(self, article_id):
        return {
            "id": str(article_id),
            "type": "article",
            "publication": "The Guardian",
            "headline": "Mock headline %s" % article_id,
            "standfirst": "Mock standfirst %s" % article_id,
            "byline": "Mock Byline",
            "sectionName": "Mock section",
            "trailText": "Mock trailText %s" % article_id,
            "linkText": "Mock linkText %s" % article_id,
            "webUrl": "http://www.guardian.co.uk/fake-url/%s" % article_id,
            "gdnUrl": "http://mockgdnapi/content/item/%s" % article_id,
            "publicationDate": "2009-03-01T00:00:00",
            "typeSpecific": {
                "@class": "article",
                "body": "Mock content for article %s" % article_id,
            },
            "tags": self.fake_tags(article_id)
        }
    
    def fake_tags(self, article_id):
        return [{
            "name": "Article",
            "type": "content-type",
            "filter": "/global/article",
            "gdnUrl": "http://mockgdnapi/content/search?filter=/global/article",
            "webUrl": "http://www.guardian.co.uk/global/article"
        } for i in range(4)]

