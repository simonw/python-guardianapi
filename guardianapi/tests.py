import client, mockapi
import unittest

class SearchTestCase(unittest.TestCase):
    api_key = 'fake-api-key'
    
    def setUp(self):
        self.fetcher = mockapi.MockFetcher()
        self.client = self.make_client(self.api_key)
    
    def tearDown(self):
        self.fetcher.reset()
    
    def make_client(self, api_key):
        return client.Client(api_key, fetcher = self.fetcher)
    
    def assertIn(self, needle, haystack):
        self.assert_(needle in haystack, "Expected to find '%s' in '%s'" % (
            needle, haystack
        ))
    
    def test_mock_fetcher(self):
        "MockFetcher should intercept and record URL retrieval attempts"
        search_term = 'hello'
        self.assertEqual(len(self.fetcher.fetched), 0)
        results = self.client.search(q = search_term)
        self.assertEqual(len(self.fetcher.fetched), 1)
        self.assertEqual(self.fetcher.fetched[0][1]['q'], search_term)
    
    def test_api_key(self):
        "api_key given to Client constructor should be handled automatically"
        results = self.make_client(api_key = 'foo').search()
        self.assertEqual(self.fetcher.fetched[-1][1]['api_key'], 'foo')
        results = self.make_client(api_key = 'bar').search()
        self.assertEqual(self.fetcher.fetched[-1][1]['api_key'], 'bar')
    
    def test_tags(self):
        "tags() method should return tags"
        self.assertEqual(len(self.fetcher.fetched), 0)
        results = self.client.tags(count = 20)
        self.assertEqual(len(self.fetcher.fetched), 1)
        self.assertIn('all-subjects', self.fetcher.fetched[-1][0])
        self.assertEqual(len(list(results)), 20)
    
    def test_search(self):
        "search() method should return results and filters"
        results = self.client.search(q = 'foo', count = 20)
        self.assertEqual(len(results.results()), 20)
        self.assert_(isinstance(results.filters(), list))
    
    def test_all_results(self):
        return
        "results.all() should magically paginate"
        self.fetcher.fake_total_results = 101
        results = self.client.search(q = 'foo')
        self.assertEqual(len(results.results()), 20)
        all_results = list(results.all(sleep = 0))
        self.assertEqual(len(all_results), 101)

if __name__ == '__main__':
    unittest.main()
