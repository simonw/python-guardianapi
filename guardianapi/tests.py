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
    
    def test_mock_fetcher(self):
        "MockFetcher should intercept and record URL retrieval attempts"
        search_term = 'hello'
        self.assertEqual(len(self.fetcher.fetched), 0)
        results = self.client.search(q = search_term)
        self.assertEqual(len(self.fetcher.fetched), 1)
        self.assertEqual(self.fetcher.fetched[0][1]['q'], search_term)
    
    def test_api_key(self):
        "api_key given to Client constructor should be handled automatically"
        results = self.make_client('foo').search()
        self.assertEqual(self.fetcher.fetched[-1][1]['api_key'], 'foo')
        results = self.make_client('bar').search()
        self.assertEqual(self.fetcher.fetched[-1][1]['api_key'], 'bar')

if __name__ == '__main__':
    unittest.main()
