Sunny
=====

This is a very simple Solr interface for Python.

Installation
------------

```bash
$ pip install sunny
```

Usage
-----

Create your Solr connection (actually a pool of connections) and then
pass query parameters using simple dictionaries.  The raw Solr result
is returned as a Python dictionary.

```python
>>> import sunny
>>> solr = sunny.Solr('http://localhost:8080/solr')
>>> solr.query({'q': 'office',
...             'facet': 'on',
...             'facet.field': ['network', 'runtime']})
{u'responseHeader': {u'status': 0, u'QTime': ...
```

Parameters
----------

Solr parameters are passed as dictionaries where every value may be
either a string or a list of strings.

``wt=json`` is passed with every request no matter what, because JSON
is easy to convert to Python objects.

Example:

```python
>>> import sunny
>>> solr = sunny.Solr('http://localhost:8080/solr')
>>> solr.query({'q': 'office',
...             'facet': 'on',
...             'facet.field': ['network', 'runtime']})
{u'responseHeader': {u'status': 0, u'QTime': ...
```

The above is equivalent to this query string:
``?wt=json&q=office&facet=on&facet.field=network&facet.field=runtime``

If the ``orderedmultidict`` package is installed, you may use
``omdict`` instances instead of dictionaries.

License
-------

BSD
