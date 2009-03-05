Usage
=====

>>> from guardianapi import Client
>>> client = Client('my-api-key-goes-here')
>>> results = client.search(q = 'ocelots')
>>> results.count()
36
>>> for item in results.results():
...     print item['headline']

This will return the first ten results. To retrieve everything (by 
paginating across all pages automatically), do the following:

>>> for item in results.all():
...     print item['headline']

To access the filters for a result set:

>>> for filter in results.filters():
...    print filter

Some API responses include URLs to make further requests. Here's how to start
a request using a full API URL:

>>> url = results.filters()[0]['apiUrl']
>>> new_results = client.request(url)
