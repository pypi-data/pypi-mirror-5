Sunny
=====

This is a very simple Solr interface for Python.


Usage
-----

    >> import sunny
    >> solr = sunny.Solr('http://localhost:8080/solr')
    >> solr.query({'q': 'office'})
    {u'responseHeader': {u'status': 0, u'QTime': ...


Parameters
----------

Solr parameters are passed as dictionaries where every value may be
either a string or a list of strings.

Example:

    {'q': 'office',
     'facet': 'on',
     'facet.field': ['network', 'runtime']}
    ==>
    ?q=office&facet=on&facet.field=network&facet.field=runtime

If ``omdict`` is installed, you may use ``omdict`` instances instead.

``wt=json`` is passed with every request no matter what.


License
-------

BSD
