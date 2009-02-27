import simplejson, urllib, urlparse

def jsonpath_tiny(json, path):
    # A subset of http://goessner.net/articles/JsonPath/
    if not path.startswith('$.'):
        raise TypeError, 'JSONPath must start with $.'
    for bit in path[2:].split('.'):
        json = json[bit]
    return json

# Syntactic sugar enabling classes
class AttrDictList(list):
    def transform(self, value):
        if isinstance(value, dict):
            return AttrDict(value)
        elif isinstance(value, list):
            return AttrDictList(value)
        else:
            return value
    
    def __getitem__(self, index):
        value = super(AttrDictList, self).__getitem__(index)
        return self.transform(value)
    
    def __iter__(self):
        for value in super(AttrDictList, self).__iter__():
            yield self.transform(value)
    
class AttrDict(dict):
    def __getattr__(self, key):
        try:
            value = self[key]
        except KeyError:
            raise AttributeError, key
        if isinstance(value, dict):
            value = AttrDict(value)
        if isinstance(value, list):
            value = AttrDictList(value)
        return value

class Result(object):
    def __init__(self, client, url, json, jsonpath):
        self.client = client
        self.url = url
        self.json = json
        self.jsonpath = jsonpath
    
    def __iter__(self):
        for result in jsonpath_tiny(self.json, self.jsonpath):
            yield AttrDict(result)

class Client(object):
    def __init__(self, fp):
        json = simplejson.load(fp)
        self.endpoints = json['endpoints']
        self.base_url = json['base_url']
        # Create the methods
        for id, endpoint in self.endpoints.items():
            setattr(self, id, self.make_method(id, endpoint))
    
    def fetch_url(self, url, definition):
        json = simplejson.load(urllib.urlopen(url))
        return Result(self, url, json, definition['results'])
    
    def make_method(self, id, json):
        params = json.get('params', {})
        endpoint_url = urlparse.urljoin(self.base_url, json['url'])
        def method(**args):
            args = dict([self.transform_arg(k, v) for k, v in args.items()])
            # Check for required arguments
            required = [
                key for key, value in params.items() if value.get('required')
            ]
            missing = [a for a in required if a not in args]
            if missing:
                raise TypeError, (
                    'Missing required arguments: %s' % ', '.join(missing)
                )
            # Check for unrecognised arguments
            unrecognised = [
                a for a in args if a not in params
            ]
            if unrecognised:
                raise TypeError, (
                    'Unrecognised arguments: %s' % ', '.join(unrecognised)
                )
            # Construct URL
            url = endpoint_url
            
            args['format'] = 'json'
            if args:
                url += '?' + urllib.urlencode(args)
            
            return self.fetch_url(url, json)
        
        method.__name__ = id
        method.__doc__ = json.get('description', '')
        return method
    
    def transform_arg(self, key, value):
        return key, value

class TestableClient(Client):
    def fetch_url(self, url):
        return url

class GuardianContent(Client):
    
    def __init__(self):
        super(GuardianContent, self).__init__(open('index.json'))
    
    def transform_arg(self, key, value):
        return key.replace('_', '-'), value
