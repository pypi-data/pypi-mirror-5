rawes
=====

About
-----
rawes is an elasticsearch driver for Python.  It provides a small level of abstraction above the requests library - enough abstraction to be useful, but not so much to obscure elasticsearch's great [native api](http://www.elasticsearch.org/guide/reference/api/)

Features
--------
* elasticsearch native API support
* Python 3 support
* gzip over HTTP support
* HTTPS support
* Thrift support

Installation
------------
```bash
$ pip install rawes
```

Usage
-----
Create a connection to elasticsearch
```python
import rawes
es = rawes.Elastic('localhost:9200')
```

Search for a document
```python
es.get('tweets/tweet/_search', data={
    'query' : {
        'match_all' : {}
    }
})
```

The rawes.Elastic constructor takes the following parameters (defaults shown):
```python
rawes.Elastic(
    url='http://localhost:9200',    # Protocol, host, and port of elasticsearch service. 
                                    # Valid protocols: http, https, thrift
                                    # Default protocol is http, unless port is in range 9500-9600, then thrift
                                    # Default ports: http=9200, https=443, thrift=9500
    timeout=30,                     # Timeout in seconds,
    **kwrgs                         # http(s) only: additional parameters you wish to pass 
                                    # to the python 'requests' library (for example, basic auth)
)
```

Constructor examples:

```python
es = rawes.Elastic()                        # will connect to: http://localhost:9200
es = rawes.Elastic('https://localhost')     # will connect to: https://localhost:443
es = rawes.Elastic('thrift://localhost')    # will connect to: thrift://localhost:9500
es = rawes.Elastic('https://example.org:8443', auth=('user','pass'))  # https with basic auth connection to: https://example.org:8443
```

An instance of rawes.Elastic ('es' in this case) has methods for get, post, put, delete, and head (for each http verb).  Each method takes the following parameters (defaults shown):
```python
es.get(
    path='',    # http URL path
    data='',    # http body.  can be either a string or a python dictionary (will automatically be converted to JSON)
    params={},  # http URL params passed as a python dictionary
    headers={}, # http headers as a python dictionary
    **kwargs    # additional parameters you wish to pass to the python 'requests' library or the thrift RestRequest
                # Examples: headers, basic auth
)
```

Examples
--------

Create a new document in the twitter index of type tweet with id 1
```python
es.put('tweets/tweet/1', data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T08:00:30Z',
    'message' : 'Tweeting about elasticsearch'
})
es.put('blogs/post/2', data={
    'user' : 'dan',
    'post_date' : '2012-8-27T09:30:03Z',
    'title' : 'Elasticsearch',
    'body' : 'Blogging about elasticsearch'
})
```

Search for a document, specifying http params
```python
es.get('tweets/tweet/_search', data={
    'query' : {
        'match_all' : {}
    }
}, params= {
    'size': 2
})
```

Search for a document with a JSON string
```python
es.get('tweets,blogs/_search', data="""
{
    "query" : {
        "match_all" : {}
    }
}
""")
```

Update a document
```python
es.put('someindex/sometype/123', data={
    'value' : 100,
    'other' : 'stuff'
})
es.post('someindex/sometype/123/_update', data={
    'script' : 'ctx._source.value += value',
    'params' : {
        'value' : 50
    }
})
```

Delete a document
```python
es.delete('tweets/tweet/1')
```

Bulk load
```python
bulk_body = '''
{"index" : {}}
{"key":"value1"}
{"index" : {}}
{"key":"value2"}
{"index" : {}}
{"key":"value3"}
'''

es.post('someindex/sometype/_bulk', data=bulk_body)

bulk_list = [
    {"index" : {}},
    {"key":"value4"},
    {"index" : {}},
    {"key":"value5"},
    {"index" : {}},
    {"key":"value6"}
]

# Remember to include the trailing \n character for bulk inserts
bulk_body_2 = '\n'.join(map(json.dumps, bulk_list))+'\n'

es.post('someindex/sometype/_bulk', data=bulk_body_2)
```


Alternate Syntax
----------------
Instead of setting the first argument of a es.&lt;http verb&gt; call to the HTTP URL path, you can also use python attributes and item accessors to build up the url path. For example:
```python
es.post('tweets/tweet/', data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T09:15:59',
    'message' : 'More tweets about elasticsearch'
})
```

Becomes:
```python
es.tweets.tweet.post(data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T09:15:59',
    'message' : 'More tweets about elasticsearch'
})
```

Or using item accessors ([] notation).  This can be useful for characters that are not allowed in python attributes:
```python
es['tweets']['tweet'].post(data={
    'user' : 'dwnoble',
    'post_date' : '2012-8-27T09:15:59',
    'message' : 'More tweets about elasticsearch'
})
```

More examples:

Searching the "tweets" index for documents of type "tweets"
```python
es.tweets.tweet._search.get(data={'query' : {'match_all' : {} }})
```

Searching the "tweets" and "blogs" index for documents of any type using a JSON strings
```python
es['tweets,blogs']._search.get(data='{"query" : {"match_all" : {}}}')
```

JSON Encoding
-------------

By default, rawes will encode datetimes (timezone required!) to UTC ISO8601 strings with 'second' precision before handing the JSON off to elasticsearch.  If elasticsearch has no mapping defined, this will result in the default mapping of 'dateOptionalTime.'  
Timezones are required for this automatic serialization: you may want to use a python module like python-dateutil (Python 2.x only) or pytz to make your life easier.
```python
from datetime import datetime
from dateutil import tz
eastern_timezone = tz.gettz('America/New_York')

es.put('tweets/tweet/99', data={
    'user' : 'dwnoble',
    'post_date' : datetime(2012, 8, 27, 8, 0, 30, tzinfo=eastern_timezone),
    'message' : 'Tweeting about elasticsearch'
})

es.get('tweets/tweet/99')['_source']['post_date']
# Returns:
u'2012-08-27T12:00:30Z'
```

Alternatively, you can specify a custom JSON encoder using the json_encoder parameter:
```python
from datetime import datetime
from dateutil import tz
eastern_timezone = tz.gettz('America/New_York')

def encode_custom(obj):
    if isinstance(obj, datetime):
        return obj.astimezone(tz.tzutc()).strftime('%Y-%m-%d')
    raise TypeError(repr(obj) + " is not JSON serializable")

es.put('tweets/tweet/445', data={
    'user' : 'dwnoble',
    'post_date' : datetime(2012, 11, 12, 9, 45, 45, tzinfo=eastern_timezone),
    'message' : 'Tweeting about elasticsearch'
}, json_encoder=encode_custom)

es.get('tweets/tweet/445')['_source']['post_date']
# Returns:
u'2012-11-12'
```

Error Handling
--------------
As of version 0.5, the rawes.Elastic constructor throws a rawes.elastic_exception.ElasticException any time elasticsearch returns an http status code of 400 or greater.

```python
from rawes.elastic_exception import ElasticException
es = rawes.Elastic('localhost:9200')
try:
    es.get('invalid_index/invalid_type/123')
except ElasticException as e:
    # since our index is invalid, this exception handler will run  
    print e.result 
    # prints: {u'status': 404, u'error': u'IndexMissingException[[invalid_index] missing]'}
    print e.status_code
    # prints: 404
```

Thrift support
--------------
Thrift is supported for Python 2.x versions only.  Before thrift will work with rawes, you must install the thrift python module
```bash
$ pip install thrift
```

By default, connections on ports between 9500 and 9600 will use thrift
```python
import rawes
es_thrift = rawes.Elastic('localhost:9500')
```

If you are using thrift on a non standard port, specify a 'thrift://' url
```python
import rawes
es_thrift = rawes.Elastic('thrift://localhost:8500')
```

Run Unit Tests
--------------
rawes' unit tests require the python thrift module to run:
```bash
$ pip install thrift
```

Run tests:
```bash
$ python -m unittest tests
```

Run tests for Python 3 (no thrift tests, no need to "pip install thrift")
```bash
$ python3 -m unittest tests.py3k
```

License
-------
Apache 2.0 License

Contact
-------
[@dwnoble](https://twitter.com/dwnoble)
