class APIError(Exception):
    pass

class APIKeyError(APIError):
    def __init__(self, api_key, e):
        self.api_key = api_key
        self.wrapped_exception = e

    def __repr__(self):
        return '<APIKeyError: %s is a bad API key>' % self.api_key

class ItemNotFound(APIError):
    def __init__(self, item_id):
        self.item_id = item_id
    
    def __repr__(self):
        return '<ItemNotFoundError: %s>' % self.item_id

class URLNotRecognised(APIError):
    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return '<URLNotRecognised: %s>' % self.url

class HTTPError(APIError):
    def __init__(self, status_code, info=None):
        self.status_code = status_code
        self.info = info

    def __repr__(self):
        return '<HTTPError: %s>' % self.status_code
