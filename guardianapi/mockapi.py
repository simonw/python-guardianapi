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
    
    def get(self, url):
        bits = urlparse.urlparse(url)
        endpoint = bits.path.split('/')[-1]
        
        args = cgi.parse_qs(bits.query)
        # foo=bar becomes {'foo': ['bar']} - collapse single values
        for key in args:
            if isinstance(args[key], list) and len(args[key]) == 1:
                args[key] = args[key][0]
        
        method = getattr(self, 'do_%s' % endpoint.replace('-', '_'))
        json = method(**args)
        
        self.fetched.append((url, args))
        return {}, simplejson.dumps(json, indent=4)
    
    def do_search(self, **kwargs):
        startIndex = kwargs.get('startIndex', 0)
        per_page = 20
        return {
            "search": {
                "count": 101,
                "startIndex": startIndex,
                "results": [
                    self.fake_article(article_id) 
                    for article_id in range(startIndex, startIndex + per_page)
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
    
    def do_content(self, rest_of_url, **kwargs):
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
            "gdnUrl": "http://mockgdnapi/content/content/%s" % article_id,
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

