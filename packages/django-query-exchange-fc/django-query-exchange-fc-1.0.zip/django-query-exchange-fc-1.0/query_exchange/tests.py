from django.template import Template, Context
from django.utils.datastructures import MultiValueDict
from django.conf.urls.defaults import *

from query_exchange import reverse_with_query, process_query

def test_view(request):
    pass

urlpatterns = patterns('',
    url(r'^test_url/(\d+)/$', test_view, name='test_url'),
)

class Request(object):
    def __init__(self, data):
        self.GET = MultiValueDict(data)

request = Request({'b': [1, 2], 'c': [4]})

__test__ = {
    'process_query': """
        >>> process_query(request.GET)
        'b=1&b=2&c=4'

        >>> process_query(request.GET, keep=['b'], add={'page': 3})
        'b=1&b=2&page=3'

        >>> process_query(request.GET, add={'page': 3})
        'b=1&b=2&c=4&page=3'

        >>> process_query(request.GET, exclude=['b'], add={'page': 3})
        'c=4&page=3'

        >>> process_query(request.GET)
        'b=1&b=2&c=4'

        >>> process_query(request.GET, keep=['c'], add={'c': 5}, exclude=['b'])
        'c=4&c=5'

        >>> process_query(request.GET, add={'c': 'foobar'}, exclude=['b'])
        'c=foobar'

        >>> process_query(request.GET, keep=['b', 'c'], remove={'b': 1})
        'b=2&c=4'
    """,
    'reverse_with_query': """
        >>> reverse_with_query('test_url', args=(1,), params=request.GET, keep=['b'], add={'page': 3})
        '/test_url/1/?b=1&b=2&page=3'
        >>> reverse_with_query('test_url', args=(1,), params={}, add={'page': 3})
        '/test_url/1/?page=3'

    """,
    'url_with_query': """
        >>> def render(line):
        ...     tmpl = Template('''
        ...            {%% load query_exchange_tags %%}
        ...            %s
        ...     ''' % line)
        ...     return tmpl.render(Context({'request': request})).strip().encode('utf-8')

        >>> render('{% url_with_query "test_url" 1 keep "b" add page=3 %}')
        '/test_url/1/?b=1&amp;b=2&amp;page=3'

        >>> render('{% url_with_query "test_url" 1 %}')
        '/test_url/1/?b=1&amp;b=2&amp;c=4'

        >>> render('{% url_with_query "test_url" 1 exclude "c" add page=3 as saved_url %}{{ saved_url|safe }}')
        '/test_url/1/?b=1&amp;b=2&amp;page=3'

        >>> render('{% url_with_query "test_url" 1 add page=3 %}')
        '/test_url/1/?b=1&amp;b=2&amp;c=4&amp;page=3'

        >>> render('{% url_with_query "test_url" 1 remove b=1 %}')
        '/test_url/1/?b=2&amp;c=4'

        >>> render('{% url_with_query "test_url" 1 keep "b","c" remove b=2 add page=3 %}')
        '/test_url/1/?b=1&amp;c=4&amp;page=3'

    """,
    'with_query': """
        >>> def render(line):
        ...     tmpl = Template('''
        ...            {%% load query_exchange_tags %%}
        ...            %s
        ...     ''' % line)
        ...     return tmpl.render(Context({'request': request, 'concrete_url': '/test_url/1/'})).strip().encode('utf-8')

        >>> render('{% with_query concrete_url keep "b" add page=3 %}')
        '/test_url/1/?b=1&amp;b=2&amp;page=3'

        Passthrough all query params
        >>> render('{% with_query concrete_url %}')
        '/test_url/1/?b=1&amp;b=2&amp;c=4'

        This exists query string in base url
        >>> render('{% with_query "/test_url/1/?d=5" keep "b","d" add page=3 %}')
        '/test_url/1/?b=1&amp;b=2&amp;d=5&amp;page=3'
        >>> render('{% with_query "/test_url/1/?d=5" keep "b","d" remove b=2 add page=3 %}')
        '/test_url/1/?b=1&amp;d=5&amp;page=3'
    """
}
