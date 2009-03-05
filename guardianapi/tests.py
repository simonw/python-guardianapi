import client, mockapi
import unittest

class BaseTestCase(unittest.TestCase):
    api_key = 'fake-api-key'
    
    def setUp(self):
        self.fetcher = mockapi.MockFetcher()
        self.client = self.make_client(self.api_key)
    
    def tearDown(self):
        self.fetcher.reset()
    
    def make_client(self, api_key):
        return client.Client(api_key, fetcher = self.fetcher)
    
    def assertRequestCount(self, count):
        self.assertEqual(len(self.fetcher.fetched), count, 
            "Expected %d HTTP requests, got %d" % (
                count, len(self.fetcher.fetched)
            )
        )
    
    def assertIn(self, needle, haystack):
        self.assert_(needle in haystack, "Expected to find '%s' in '%s'" % (
            needle, haystack
        ))
    
class MockFetcherTestCase(BaseTestCase):
    
    def test_mock_fetcher(self):
        "MockFetcher should intercept and record URL retrieval attempts"
        search_term = 'hello'
        self.assertRequestCount(0)
        results = self.client.search(q = search_term)
        self.assertRequestCount(1)
        self.assertEqual(self.fetcher.fetched[0][1]['q'], search_term)
    
    def test_mock_fetcher_correct_pagination(self):
        "start-index=90&count=30 on a 101 sized result set should return 11"
        self.fetcher.fake_total_results = 101
        self.assertRequestCount(0)
        results = self.client.search(start_index = 90, count = 30)
        self.assertEqual(results.start_index(), 90)
        self.assertEqual(results.count(), 101)
        self.assertRequestCount(1)
        self.assertEqual(len(results.results()), 11)

class ClientTestCase(BaseTestCase):
    
    def test_results_has_next(self):
        "results.has_next() should give the correct answers"
        class MockResults(client.Results):
            def __init__(self, total_results, start_index, per_page):
                self._total_results = total_results
                self._start_index = start_index
                self._per_page = per_page
                self.kwargs = {'count': per_page, 'start_index': start_index}
            
            def count(self):
                return self._total_results
            
            def start_index(self):
                return self._start_index
        
        r = MockResults(total_results = 10, start_index = 0, per_page = 20)
        self.assert_(not r.has_next())
        
        r = MockResults(total_results = 10, start_index = 0, per_page = 5)
        self.assert_(r.has_next())
        
        r = MockResults(total_results = 101, start_index = 90, per_page = 10)
        self.assert_(r.has_next())
        
        r = MockResults(total_results = 101, start_index = 100, per_page = 10)
        self.assert_(not r.has_next())
    
    def test_api_key(self):
        "api_key given to Client constructor should be handled automatically"
        results = self.make_client(api_key = 'foo').search()
        self.assertEqual(self.fetcher.fetched[-1][1]['api_key'], 'foo')
        results = self.make_client(api_key = 'bar').search()
        self.assertEqual(self.fetcher.fetched[-1][1]['api_key'], 'bar')
    
    def test_tags(self):
        "tags() method should return tags"
        self.assertRequestCount(0)
        results = self.client.tags(count = 20)
        self.assertRequestCount(1)
        self.assertIn('tags', self.fetcher.fetched[-1][0])
        self.assertEqual(len(list(results)), 20)
    
    def test_search(self):
        "search() method should return results and filters"
        results = self.client.search(q = 'foo', count = 20)
        self.assertEqual(len(results.results()), 20)
        self.assert_(isinstance(results.filters(), list))
    
    def test_all_search(self):
        "search().all() should magically paginate"
        self.fetcher.fake_total_results = 101
        self.assertRequestCount(0)
        results = self.client.search(q = 'foo', count = 30)
        self.assertRequestCount(1)
        self.assertEqual(len(results.results()), 30)
        all_results = list(results.all(sleep = 0))
        self.assertRequestCount(4)
        self.assertEqual(len(all_results), 101)
    
    def test_all_tags(self):
        "tags().all() should magically paginate"
        self.fetcher.fake_total_results = 301
        self.assertRequestCount(0)
        results = self.client.tags(count = 100)
        self.assertRequestCount(1)
        self.assertEqual(len(results.results()), 100)
        all_tags = list(results.all(sleep = 0))
        self.assertRequestCount(4)
        self.assertEqual(len(all_tags), 301)
    
    def test_request_search(self):
        "client.request(url-to-search-results) should work correctly"
        url = 'http://gdn/content/search?q=obama'
        self.assertRequestCount(0)
        results = self.client.request(url)
        self.assertEqual(results.kwargs['q'][0], 'obama')
        self.assertRequestCount(1)
        self.assert_(isinstance(results, client.SearchResults))
    
    def test_request_content(self):
        "client.fetch(url-to-content) should work correctly"
        url = 'http://gdn/content/item/123'
        self.assertRequestCount(0)
        results = self.client.request(url)
        self.assertRequestCount(1)
        self.assert_(isinstance(results, dict))
        self.assertEqual(results['id'], '123')

if __name__ == '__main__':
    unittest.main()
