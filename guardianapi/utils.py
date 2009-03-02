def jsonpath(json, path):
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
