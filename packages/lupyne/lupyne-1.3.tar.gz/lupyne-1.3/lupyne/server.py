"""
Restful json `CherryPy <http://cherrypy.org/>`_ server.

The server script mounts a `WebSearcher`_ (read_only) or `WebIndexer`_ root.
Standard `CherryPy configuration <http://docs.cherrypy.org/stable/concepts/config.html>`_ applies,
and the provided `custom tools <#tools>`_ are also configurable.
All request and response bodies are `application/json values <http://tools.ietf.org/html/rfc4627.html#section-2.1>`_.

WebSearcher exposes resources for an IndexSearcher.
In addition to search requests, it provides access to term and document information in the index.

 * :meth:`/ <WebSearcher.index>`
 * :meth:`/search <WebSearcher.search>`
 * :meth:`/docs <WebSearcher.docs>`
 * :meth:`/terms <WebSearcher.terms>`
 * :meth:`/update <WebSearcher.update>`

WebIndexer extends WebSearcher, exposing additional resources and methods for an Indexer.
Single documents may be added, deleted, or replaced by a unique indexed field.
Multiples documents may also be added or deleted by query at once.
By default changes are not visible until the update resource is called to commit a new index version.
If a near real-time Indexer is used, then changes are instantly searchable.
In such cases a commit still hasn't occurred, and the index based :meth:`last-modified header <validate>` shouldn't be used for caching.

 * :meth:`/ <WebIndexer.index>`
 * :meth:`/search <WebIndexer.search>`
 * :meth:`/docs <WebIndexer.docs>`
 * :meth:`/fields <WebIndexer.fields>`
 * :meth:`/update <WebIndexer.update>`

Custom servers should create and mount WebSearchers and WebIndexers as needed.
:meth:`Caches <WebSearcher.update>` and :meth:`field settings <WebIndexer.fields>` can then be applied directly before `starting <#start>`_ the server.
WebSearchers and WebIndexers can of course also be subclassed for custom interfaces.

CherryPy and Lucene VM integration issues:
 * Monitors (such as autoreload) are not compatible with the VM unless threads are attached.
 * WorkerThreads must be also attached to the VM.
 * VM initialization must occur after daemonizing.
 * Recommended that the VM ignores keyboard interrupts (-Xrs) for clean server shutdown.
"""

from future_builtins import map
import re
import time
import uuid
import socket, httplib
import heapq
import collections
import itertools
import os, optparse
from email.utils import formatdate
import contextlib
try:
    import simplejson as json
except ImportError:
    import json
import warnings
import lucene
try:
    from org.apache.lucene import search
except ImportError:
    search = lucene
import cherrypy
try:
    from . import engine, client
except ValueError:
    import engine, client

if cherrypy.__version__ < '3.2':
    warnings.warn('Support for cherrypy 3.1 will be removed in the next release.', DeprecationWarning)

def tool(hook):
    "Return decorator to register tool at given hook point."
    def decorator(func):
        setattr(cherrypy.tools, func.__name__, cherrypy.Tool(hook, func))
        return func
    return decorator

@tool('before_handler')
def json_in(content_type='application/json', process_body=None):
    """Handle request bodies in json format.
    
    :param content_type: request media type
    :param process_body: optional function to process body into request.params
    """
    request = cherrypy.serving.request
    media_type = request.headers.get('content-type')
    if media_type == content_type:
        with HTTPError(httplib.BAD_REQUEST, ValueError, AttributeError):
            request.json = json.load(request.body)
        if process_body is not None:
            with HTTPError(httplib.BAD_REQUEST, TypeError):
                request.params.update(process_body(request.json))
    elif media_type:
        message = "Expected an entity of content type {0}".format(content_type)
        raise cherrypy.HTTPError(httplib.UNSUPPORTED_MEDIA_TYPE, message)

@tool('before_handler')
def json_out(content_type='application/json', indent=None):
    """Handle responses in json format.
    
    :param content_type: response content-type header
    :param indent: indentation level for pretty printing
    """
    request = cherrypy.serving.request
    request._json_inner_handler = request.handler
    headers = cherrypy.response.headers
    headers['content-type'] = content_type
    def handler(*args, **kwargs):
        body = request._json_inner_handler(*args, **kwargs)
        return json.dumps(body, indent=indent) if headers['content-type'] == content_type else body
    request.handler = handler

@tool('on_start_resource')
def allow(methods=('GET',), paths=()):
    "Only allow specified methods."
    request = cherrypy.serving.request
    if paths and hasattr(request.handler, 'args'):
        with HTTPError(httplib.NOT_FOUND, IndexError):
            methods = paths[len(request.handler.args)]
    if 'GET' in methods and 'HEAD' not in methods:
        methods += 'HEAD',
    cherrypy.response.headers['allow'] = ', '.join(methods)
    if request.method not in methods:
        raise cherrypy.HTTPError(httplib.METHOD_NOT_ALLOWED)

@tool('before_finalize')
def timer():
    "Return response time in headers."
    response = cherrypy.serving.response
    response.headers['x-response-time'] = time.time() - response.time

@tool('on_start_resource')
def validate(etag=True, last_modified=False, max_age=None, expires=None):
    """Return and validate caching headers.
    
    :param etag: return weak entity tag header based on index version and validate if-match headers
    :param last_modified: return last-modified header based on index timestamp and validate if-modified headers
    :param max_age: return cache-control max-age and age headers based on last update timestamp
    :param expires: return expires header offset from last update timestamp
    """
    root = cherrypy.request.app.root
    headers = cherrypy.response.headers
    if etag:
        headers['etag'] = 'W/"{0}"'.format(root.searcher.version)
        cherrypy.lib.cptools.validate_etags()
    if last_modified:
        headers['last-modified'] = formatdate(root.searcher.timestamp, usegmt=True)
        cherrypy.lib.cptools.validate_since()
    if max_age is not None:
        headers['age'] = int(time.time() - root.updated)
        headers['cache-control'] = 'max-age={0}'.format(max_age)
    if expires is not None:
        headers['expires'] = formatdate(expires + root.updated, usegmt=True)

@tool('before_handler')
def params(**types):
    "Convert specified request params."
    params = cherrypy.request.params
    with HTTPError(httplib.BAD_REQUEST, ValueError):
        for key in set(types).intersection(params):
            params[key] = types[key](params[key])

def multi(value):
    return value and value.split(',')

class params:
    "Parameter parsing."
    @staticmethod
    def q(searcher, q, **options):
        options = dict((key.partition('.')[-1], options[key]) for key in options if key.startswith('q.'))
        field = options.pop('field', [])
        fields = [field] if isinstance(field, basestring) else field
        fields = [name.partition('^')[::2] for name in fields]
        if any(boost for name, boost in fields):
            field = dict((name, float(boost or 1.0)) for name, boost in fields)
        elif isinstance(field, basestring):
            (field, boost), = fields
        else:
            field = [name for name, boost in fields] or ''
        if 'type' in options:
            with HTTPError(httplib.BAD_REQUEST, AttributeError):
                return getattr(engine.Query, options['type'])(field, q)
        for key in set(options) - set(['op', 'version']):
            with HTTPError(httplib.BAD_REQUEST, ValueError):
                options[key] = json.loads(options[key])
        if q is not None:
            with HTTPError(httplib.BAD_REQUEST, lucene.JavaError):
                return searcher.parse(q, field=field, **options)
    @staticmethod
    def fields(searcher, fields=None, **options):
        if fields is not None:
            fields = dict.fromkeys(fields)
        multi = options.get('fields.multi', ())
        indexed = (field.split(':') for field in options.get('fields.indexed', ()))
        indexed = dict((item[0], searcher.comparator(*item)) for item in indexed)
        return fields, multi, indexed

def json_error(version, **body):
    "Transform errors into json format."
    tool = cherrypy.request.toolmaps['tools'].get('json_out', {})
    cherrypy.response.headers['content-type'] = tool.get('content_type', 'application/json')
    return json.dumps(body, indent=tool.get('indent'))

def attach_thread(id=None):
    "Attach current cherrypy worker thread to lucene VM."
    lucene.getVMEnv().attachCurrentThread()

class Autoreloader(cherrypy.process.plugins.Autoreloader):
    "Autoreload monitor compatible with lucene VM."
    def run(self):
        attach_thread()
        cherrypy.process.plugins.Autoreloader.run(self)

class AttachedMonitor(cherrypy.process.plugins.Monitor):
    "Periodically run a callback function in an attached thread."
    def __init__(self, bus, callback, frequency=cherrypy.process.plugins.Monitor.frequency):
        def run():
            attach_thread()
            callback()
        cherrypy.process.plugins.Monitor.__init__(self, bus, run, frequency)
    def subscribe(self):
        cherrypy.process.plugins.Monitor.subscribe(self)
        if cherrypy.engine.state == cherrypy.engine.states.STARTED:
            self.start()
    def unsubscribe(self):
        cherrypy.process.plugins.Monitor.unsubscribe(self)
        self.thread.cancel()

@contextlib.contextmanager
def HTTPError(status, *exceptions):
    "Interpret exceptions as an HTTPError with given status code."
    try:
        yield
    except exceptions as exc:
        raise cherrypy.HTTPError(status, str(exc))

class WebSearcher(object):
    """Dispatch root with a delegated Searcher.
    
    :param hosts: ordered hosts to synchronize with
    """
    _cp_config = dict.fromkeys(map('tools.{0}.on'.format, ['gzip', 'accept', 'json_in', 'json_out', 'allow', 'timer', 'validate']), True)
    _cp_config.update({'error_page.default': json_error, 'tools.gzip.mime_types': ['text/html', 'text/plain', 'application/json'], 'tools.accept.media': 'application/json'})
    def __init__(self, *directories, **kwargs):
        self.hosts = collections.deque(kwargs.pop('hosts', ()))
        if self.hosts:
            engine.IndexWriter(*directories).close()
        self.searcher = engine.MultiSearcher(directories, **kwargs) if len(directories) > 1 else engine.IndexSearcher(*directories, **kwargs)
        self.updated = time.time()
    @classmethod
    def new(cls, *args, **kwargs):
        "Return new uninitialized root which can be mounted on dispatch tree before VM initialization."
        self = object.__new__(cls)
        self.args, self.kwargs = args, kwargs
        return self
    def close(self):
        self.searcher.close()
    def sync(self, host, path=''):
        "Sync with remote index."
        path = '/' + '{0}/update/{1}/'.format(path, uuid.uuid1()).lstrip('/')
        directory = self.searcher.path
        resource = client.Resource(host)
        names = sorted(set(resource.put(path)).difference(os.listdir(directory)))
        try:
            for name in names:
                resource.download(path + name, os.path.join(directory, name))
        finally:
            resource.delete(path)
        return names
    @cherrypy.expose
    @cherrypy.tools.json_in(process_body=dict)
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    def index(self, host='', path=''):
        """Return index information and synchronize with remote index.
        
        **GET, POST** /[index]
            Return a mapping of the directory to the document count.
            Add new segments from remote host.
            
            {"host": *string*\ [, "path": *string*]}
            
            :return: {*string*: *int*,... }
        """
        if cherrypy.request.method == 'POST':
            self.sync(host, path)
            cherrypy.response.status = httplib.ACCEPTED
        if isinstance(self.searcher, engine.MultiSearcher):
            readers = map(engine.indexers.IndexReader, self.searcher.sequentialSubReaders)
            return dict((reader.directory.toString(), reader.numDocs()) for reader in readers)
        return {self.searcher.directory.toString(): len(self.searcher)}
    @cherrypy.expose
    @cherrypy.tools.json_in(process_body=dict)
    @cherrypy.tools.allow(methods=['POST'])
    def update(self, **caches):
        """Refresh index version.
        
        **POST** /update
            Reopen searcher, optionally reloading caches, and return document count.
            
            {"filters"|"sorters"|"spellcheckers": true,... }
            
            .. versionchanged:: 1.2 request body is an object instead of an array
            
            :return: *int*
        """
        names = ()
        while self.hosts:
            host = self.hosts[0]
            try:
                names = self.sync(*host.split('/'))
                break
            except socket.error:
                client.Replicas.discard.__func__(self, host)
            except httplib.HTTPException as exc:
                assert exc[0] == httplib.METHOD_NOT_ALLOWED, exc
                break
        self.searcher = self.searcher.reopen(**caches)
        self.updated = time.time()
        if names:
            engine.IndexWriter(self.searcher.directory).close()
        if not self.hosts and hasattr(self, 'fields'):
            other = WebIndexer(self.searcher.directory, analyzer=self.searcher.analyzer)
            other.indexer.shared, other.indexer.fields = self.searcher.shared, self.fields
            app, = (app for app in cherrypy.tree.apps.values() if app.root is self)
            mount(other, app=app, autoupdate=getattr(self, 'autoupdate', 0))
        return len(self.searcher)
    @cherrypy.expose
    @cherrypy.tools.params(**dict.fromkeys(['fields', 'fields.multi', 'fields.indexed', 'fields.vector', 'fields.vector.counts'], multi))
    def docs(self, name=None, value='', **options):
        """Return ids or documents.
        
        **GET** /docs
            Return array of doc ids.
            
            :return: [*int*,... ]
        
        **GET** /docs/[*int*\|\ *chars*/*chars*]?
            Return document mapping from id or unique name and value.
            
            &fields=\ *chars*,... &fields.multi=\ *chars*,... &fields.indexed=\ *chars*\ [:*chars*],...
                optionally select stored, multi-valued, and cached indexed fields
            
            &fields.vector=\ *chars*,... &fields.vector.counts=\ *chars*,...
                optionally select term vectors with term counts
            
            :return: {*string*: null|\ *string*\|\ *number*\|\ *array*\|\ *object*,... }
        """
        searcher = self.searcher
        if not name:
            return list(searcher)
        with HTTPError(httplib.NOT_FOUND, ValueError):
            id, = searcher.docs(name, value) if value else [int(name)]
        fields, multi, indexed = params.fields(searcher, **options)
        with HTTPError(httplib.NOT_FOUND, lucene.JavaError):
            doc = searcher[id] if fields is None else searcher.get(id, *itertools.chain(fields, multi))
        result = doc.dict(*multi, **(fields or {}))
        result.update((name, indexed[name][id]) for name in indexed)
        result.update((field, list(searcher.termvector(id, field))) for field in options.get('fields.vector', ()))
        result.update((field, dict(searcher.termvector(id, field, counts=True))) for field in options.get('fields.vector.counts', ()))
        return result
    @cherrypy.expose
    @cherrypy.tools.params(count=int, start=int, fields=multi, sort=multi, facets=multi, hl=multi, mlt=int, spellcheck=int, timeout=float,
        **{'fields.multi': multi, 'fields.indexed': multi, 'facets.count': int, 'facets.min': int, 'group.count': int, 'group.limit': int, 'hl.count': int, 'mlt.fields': multi})
    def search(self, q=None, count=None, start=0, fields=None, sort=None, facets='', group='', hl='', mlt=None, spellcheck=0, timeout=None, **options):
        """Run query and return documents.
        
        **GET** /search?
            Return array of document objects and total doc count.
            
            &q=\ *chars*\ &q.type=[term|prefix|wildcard]&q.\ *chars*\ =...,
                query, optional type to skip parsing, and optional parser settings: q.field, q.op,...
            
            &filter=\ *chars*
                | cached filter applied to the query
                | if a previously cached filter is not found, the value will be parsed as a query
            
            &count=\ *int*\ &start=0
                maximum number of docs to return and offset to start at
            
            &fields=\ *chars*,... &fields.multi=\ *chars*,... &fields.indexed=\ *chars*\ [:*chars*],...
                only include selected stored fields; multi-valued fields returned in an array; indexed fields with optional type are cached
            
            &sort=\ [-]\ *chars*\ [:*chars*],... &sort.scores[=max]
                | field name, optional type, minus sign indicates descending
                | optionally score docs, additionally compute maximum score
            
            &facets=\ *chars*,... &facets.count=\ *int*\&facets.min=0
                | include facet counts for given field names; facets filters are cached
                | optional maximum number of most populated facet values per field, and minimum count to return
            
            &group=\ *chars*\ [:*chars*]&group.count=1&group.limit=\ *int*
                | group documents by field value with optional type, up to given maximum count
                | limit number of groups which return docs
            
            &hl=\ *chars*,... &hl.count=1&hl.tag=strong&hl.enable=[fields|terms]
                | stored fields to return highlighted
                | optional maximum fragment count and html tag name
                | optionally enable matching any field or any term
            
            &mlt=\ *int*\ &mlt.fields=\ *chars*,... &mlt.\ *chars*\ =...,
                | doc index (or id without a query) to find MoreLikeThis
                | optional document fields to match
                | optional MoreLikeThis settings: mlt.minTermFreq, mlt.minDocFreq,...
            
            &spellcheck=\ *int*
                | maximum number of spelling corrections to return for each query term, grouped by field
                | original query is still run; use q.spellcheck=true to affect query parsing
            
            &timeout=\ *number*
                timeout search after elapsed number of seconds
            
            :return:
                | {
                | "query": *string*\|null,
                | "count": *int*\|null,
                | "maxscore": *number*\|null,
                | "docs": [{"__id__": *int*, "__score__": *number*, "__keys__": *array*,
                    "__highlights__": {*string*: *array*,... }, *string*: *value*,... },... ],
                | "facets": {*string*: {*string*: *int*,... },... },
                | "groups": [{"count": *int*, "value": *value*, "docs": [*object*,... ]},... ]
                | "spellcheck": {*string*: {*string*: [*string*,... ],... },... },
                | }
        """
        searcher = self.searcher
        if sort is not None:
            sort = (re.match('(-?)(\w+):?(\w*)', field).groups() for field in sort)
            sort = [(name, (type or 'string'), (reverse == '-')) for reverse, name, type in sort]
            with HTTPError(httplib.BAD_REQUEST, AttributeError):
                sort = [searcher.sorter(name, type, reverse=reverse) for name, type, reverse in sort]
        q = params.q(searcher, q, **options)
        qfilter = options.pop('filter', None)
        if qfilter is not None and qfilter not in searcher.filters:
            searcher.filters[qfilter] = engine.Query.__dict__['filter'](params.q(searcher, qfilter, **options))
        qfilter = searcher.filters.get(qfilter)
        if mlt is not None:
            if q is not None:
                mlt, = searcher.search(q, count=mlt+1, sort=sort)[mlt:].ids
            mltfields = options.pop('mlt.fields', ())
            with HTTPError(httplib.BAD_REQUEST, ValueError):
                attrs = dict((key.partition('.')[-1], json.loads(options[key])) for key in options if key.startswith('mlt.'))
            q = searcher.morelikethis(mlt, *mltfields, analyzer=searcher.analyzer, **attrs)
        if count is not None:
            count += start
        if count == 0:
            start = count = 1
        scores = options.get('sort.scores')
        scores = {'scores': scores is not None, 'maxscore': scores == 'max'}
        hits = searcher.search(q, filter=qfilter, count=count, sort=sort, timeout=timeout, **scores)[start:]
        result = {'query': q and unicode(q), 'count': hits.count, 'maxscore': hits.maxscore}
        tag, enable = options.get('hl.tag', 'strong'), options.get('hl.enable', '')
        hlcount = options.get('hl.count', 1)
        if hl:
            hl = dict((name, searcher.highlighter(q, name, terms='terms' in enable, fields='fields' in enable, tag=tag)) for name in hl)
        fields, multi, indexed = params.fields(searcher, fields, **options)
        if fields is None:
            fields = {}
        else:
            hits.select(*itertools.chain(fields, multi))
        with HTTPError(httplib.BAD_REQUEST, AttributeError):
            groups = hits.groupby(searcher.comparator(*group.split(':')).__getitem__) if group else [hits]
        result['groups'], limit = [], options.get('group.limit', len(groups))
        for hits in groups[:limit]:
            docs = []
            for hit in hits[:options.get('group.count', 1) if group else None]:
                doc = hit.dict(*multi, **fields)
                doc.update((name, indexed[name][hit.id]) for name in indexed)
                fragments = (hl[name].fragments(hit.id, hlcount) for name in hl)
                if hl:
                    doc['__highlights__'] = dict((name, value) for name, value in zip(hl, fragments) if value is not None)
                docs.append(doc)
            result['groups'].append({'docs': docs, 'count': len(hits), 'value': getattr(hits, 'value', None)})
        for hits in groups[limit:]:
            result['groups'].append({'docs': [], 'count': len(hits), 'value': hits.value})
        if not group:
            result['docs'] = result.pop('groups')[0]['docs']
        q = q or search.MatchAllDocsQuery()
        if facets:
            facets = (tuple(facet.split(':')) if ':' in facet else facet for facet in facets)
            facets = result['facets'] = searcher.facets(q, *facets)
            if 'facets.min' in options:
                for name, counts in facets.items():
                    facets[name] = dict((term, count) for term, count in counts.items() if count >= options['facets.min'])
            if 'facets.count' in options:
                for name, counts in facets.items():
                    facets[name] = dict((term, counts[term]) for term in heapq.nlargest(options['facets.count'], counts, key=counts.__getitem__))
        if spellcheck:
            terms = result['spellcheck'] = collections.defaultdict(dict)
            for name, value in engine.Query.__dict__['terms'](q):
                terms[name][value] = list(itertools.islice(searcher.correct(name, value), spellcheck))
        return result
    @cherrypy.expose
    @cherrypy.tools.params(count=int, step=int)
    def terms(self, name='', value=':', *path, **options):
        """Return data about indexed terms.
        
        **GET** /terms?
            Return field names, with optional selection.
            
            &option=\ *chars*
            
            :return: [*string*,... ]
        
        **GET** /terms/*chars*\[:int|float\]?step=0
            Return term values for given field name, with optional type and step for numeric encoded values.
            
            :return: [*string*,... ]
        
        **GET** /terms/*chars*/*chars*\[\*\|?\|:*chars*\|~\ *number*\]
            Return term values (wildcards, slices, or fuzzy terms) for given field name.
            
            :return: [*string*,... ]
        
        **GET** /terms/*chars*/*chars*\[\*\|~\]?count=\ *int*
            Return spellchecked term values ordered by decreasing document frequency.
            Prefixes (*) are optimized to be suitable for real-time query suggestions; all terms are cached.
            
            :return: [*string*,... ]
        
        **GET** /terms/*chars*/*chars*
            Return document count for given term.
            
            :return: *int*
        
        **GET** /terms/*chars*/*chars*/docs
            Return document ids for given term.
            
            :return: [*int*,... ]
        
        **GET** /terms/*chars*/*chars*/docs/counts
            Return document ids and frequency counts for given term.
            
            :return: [[*int*, *int*],... ]
        
        **GET** /terms/*chars*/*chars*/docs/positions
            Return document ids and positions for given term.
            
            :return: [[*int*, [*int*,... ]],... ]
        """
        searcher = self.searcher
        if not name:
            return sorted(searcher.names(**options))
        if ':' in name:
            with HTTPError(httplib.BAD_REQUEST, ValueError, AttributeError):
                name, type = name.split(':')
                type = getattr(__builtins__, type)
            return list(searcher.numbers(name, step=options.get('step', 0), type=type))
        if ':' in value:
            with HTTPError(httplib.BAD_REQUEST, ValueError):
                start, stop = value.split(':')
            return list(searcher.terms(name, start, stop or None))
        if 'count' in options:
            if value.endswith('*'):
                return searcher.suggest(name, value.rstrip('*'), options['count'])
            if value.endswith('~'):
                return list(itertools.islice(searcher.correct(name, value.rstrip('~')), options['count']))
        if '*' in value or '?' in value:
            return list(searcher.terms(name, value))
        if '~' in value:
            with HTTPError(httplib.BAD_REQUEST, ValueError):
                value, similarity = value.split('~')
                similarity = float(similarity or 0.5)
            return list(searcher.terms(name, value, minSimilarity=similarity))
        if not path:
            return searcher.count(name, value)
        if path[0] == 'docs':
            if path[1:] == ():
                return list(searcher.docs(name, value))
            if path[1:] == ('counts',):
                return list(searcher.docs(name, value, counts=True))
            if path[1:] == ('positions',):
                return list(searcher.positions(name, value))
        raise cherrypy.NotFound()

class WebIndexer(WebSearcher):
    "Dispatch root with a delegated Indexer, exposing write methods."
    def __init__(self, *args, **kwargs):
        self.indexer = engine.Indexer(*args, **kwargs)
        self.updated = time.time()
    @property
    def searcher(self):
        return self.indexer.indexSearcher
    def close(self):
        self.indexer.close()
        WebSearcher.close(self)
    def refresh(self):
        if self.indexer.nrt:
            self.indexer.refresh()
            self.updated = time.time()
        else:
            cherrypy.response.status = httplib.ACCEPTED
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    def index(self):
        """Add indexes.  See :meth:`WebSearcher.index` for GET method.
        
        **POST** /[index]
            Add indexes without optimization.
            
            [*string*,... ]
        """
        request = cherrypy.serving.request
        if request.method == 'POST':
            for directory in getattr(request, 'json', ()):
                self.indexer += directory
            self.refresh()
        return {unicode(self.indexer.directory): len(self.indexer)}
    @cherrypy.expose
    @cherrypy.tools.json_in(process_body=dict)
    @cherrypy.tools.allow(paths=[('POST',), ('GET', 'PUT', 'DELETE'), ('GET',)])
    def update(self, id='', name='', **options):
        """Commit index changes and refresh index version.
        
        **POST** /update
            Commit write operations and return document count.  See :meth:`WebSearcher.update` for caching options.
            
            {"merge": true|\ *int*,... }
            
            .. versionchanged:: 1.2 request body is an object instead of an array
            
            :return: *int*
        
        **GET, PUT, DELETE** /update/*chars*
            Verify, create, or release unique snapshot by id of current index commit and return array of referenced filenames.
            
            :return: [*string*,... ]
        
        **GET** /update/*chars*/*chars*
            Download index file corresponding to snapshot id and filename.
        """
        if not id:
            self.indexer.commit(**options)
            self.updated = time.time()
            return len(self.indexer)
        method = cherrypy.request.method
        if method == 'DELETE':
            with HTTPError(httplib.CONFLICT, lucene.JavaError):
                return self.indexer.policy.release(id)
        if method == 'PUT':
            cherrypy.response.status = httplib.CREATED
            with HTTPError(httplib.CONFLICT, lucene.JavaError):
                commit = self.indexer.policy.snapshot(id)
        else:
            with HTTPError(httplib.NOT_FOUND, lucene.JavaError):
                commit = self.indexer.policy.getSnapshot(id)
        if not name:
            return list(commit.fileNames)
        with HTTPError(httplib.NOT_FOUND, TypeError, AssertionError):
            directory = self.searcher.path
            assert name in commit.fileNames, 'file not referenced in commit'
        return cherrypy.lib.static.serve_download(os.path.join(directory, name))
    @cherrypy.expose
    @cherrypy.tools.allow(paths=[('GET', 'POST'), ('GET',), ('GET', 'PUT', 'DELETE')])
    def docs(self, name=None, value='', **options):
        """Add or return documents.  See :meth:`WebSearcher.docs` for GET method.
        
        **POST** /docs
            Add documents to index.
            
            [{*string*: *string*\|\ *number*\|\ *array*,... },... ]
        
        **PUT, DELETE** /docs/*chars*/*chars*
            Set or delete document.  Unique term should be indexed and is added to the new document.
            
            {*string*: *string*\|\ *number*\|\ *array*,... }
        """
        request = cherrypy.serving.request
        if request.method in ('GET', 'HEAD'):
            return WebSearcher.docs(self, name, value, **options)
        if request.method == 'DELETE':
            self.indexer.delete(name, value)
        elif request.method == 'PUT':
            doc = getattr(request, 'json', {})
            with HTTPError(httplib.CONFLICT, KeyError, AssertionError):
                assert self.indexer.fields[name].index.indexed, 'unique field must be indexed'
            with HTTPError(httplib.BAD_REQUEST, AssertionError):
                assert doc.setdefault(name, value) == value, 'multiple values for unique field'
            self.indexer.update(name, value, doc)
        else:
            for doc in getattr(request, 'json', ()):
                self.indexer.add(doc)
        self.refresh()
    docs._cp_config.update(WebSearcher.docs._cp_config)
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'DELETE'])
    def search(self, q=None, **options):
        """Run or delete a query.  See :meth:`WebSearcher.search` for GET method.
        
        **DELETE** /search?q=\ *chars*
            Delete documents which match query.
        """
        if cherrypy.request.method != 'DELETE':
            return WebSearcher.search(self, q, **options)
        if q is None:
            self.indexer.deleteAll()
        else:
            self.indexer.delete(params.q(self.searcher, q, **options))
        self.refresh()
    search._cp_config.update(WebSearcher.search._cp_config)
    @cherrypy.expose
    @cherrypy.tools.json_in(process_body=dict)
    @cherrypy.tools.allow(paths=[('GET',), ('GET', 'PUT')])
    @cherrypy.tools.validate(on=False)
    def fields(self, name='', **settings):
        """Return or store a field's parameters.
        
        **GET** /fields
            Return known field names.
            
            :return: [*string*,... ]
        
        **GET, PUT** /fields/*chars*
            Set and return parameters for given field name.
            
            {"store"|"index"|"termvector": *string*\|true|false,... }
            
            :return: {"store": *string*, "index": *string*, "termvector": *string*}
        """
        if not name:
            return sorted(self.indexer.fields)
        if cherrypy.request.method == 'PUT':
            if name not in self.indexer.fields:
                cherrypy.response.status = httplib.CREATED
            with HTTPError(httplib.BAD_REQUEST, AttributeError):
                self.indexer.set(name, **settings)
        with HTTPError(httplib.NOT_FOUND, KeyError):
            field = self.indexer.fields[name]
        return dict((name, str(getattr(field, name))) for name in ['store', 'index', 'termvector'])

def init(vmargs='-Xrs', **kwargs):
    "Callback to initialize VM and app roots after daemonizing."
    lucene.initVM(vmargs=vmargs, **kwargs)
    for app in cherrypy.tree.apps.values():
        if isinstance(app.root, WebSearcher):
            app.root.__init__(*app.root.__dict__.pop('args'), **app.root.__dict__.pop('kwargs'))

def mount(root, path='', config=None, autoupdate=0, app=None):
    """Attach root and subscribe to plugins.
    
    :param root,path,config: see cherrypy.tree.mount
    :param autoupdate: see command-line options
    :param app: optionally replace root on existing app
    """
    if app is None:
        app = cherrypy.tree.mount(root, path, config)
    else:
        cherrypy.engine.unsubscribe('stop', app.root.close)
        if hasattr(app.root, 'monitor'):
            app.root.monitor.unsubscribe()
        app.root = root
    cherrypy.engine.subscribe('stop', root.close)
    if autoupdate:
        root.monitor = AttachedMonitor(cherrypy.engine, root.update, autoupdate)
        root.monitor.subscribe()
    return app

def start(root=None, path='', config=None, pidfile='', daemonize=False, autoreload=0, autoupdate=0, callback=None):
    """Attach root, subscribe to plugins, and start server.
    
    :param root,path,config: see cherrypy.quickstart
    :param pidfile,daemonize,autoreload,autoupdate: see command-line options
    :param callback: optional callback function scheduled after daemonizing
    """
    cherrypy.engine.subscribe('start_thread', attach_thread)
    cherrypy.config['engine.autoreload.on'] = False
    if pidfile:
        cherrypy.process.plugins.PIDFile(cherrypy.engine, os.path.abspath(pidfile)).subscribe()
    if daemonize:
        cherrypy.config['log.screen'] = False
        cherrypy.process.plugins.Daemonizer(cherrypy.engine).subscribe()
    if autoreload:
        Autoreloader(cherrypy.engine, autoreload).subscribe()
    if callback:
        priority = (cherrypy.process.plugins.Daemonizer.start.priority + cherrypy.server.start.priority) // 2
        cherrypy.engine.subscribe('start', callback, priority)
    if root is not None:
        mount(root, path, config, autoupdate)
    cherrypy.quickstart(cherrypy.tree.apps.get(path), path, config)

parser = optparse.OptionParser(usage='python -m lupyne.server [index_directory ...]')
parser.add_option('-r', '--read-only', action='store_true', help='expose only read methods; no write lock')
parser.add_option('-c', '--config', help='optional configuration file or json object of global params')
parser.add_option('-p', '--pidfile', metavar='FILE', help='store the process id in the given file')
parser.add_option('-d', '--daemonize', action='store_true', help='run the server as a daemon')
parser.add_option('--autoreload', type=float, metavar='SECONDS', help='automatically reload modules; replacement for engine.autoreload')
parser.add_option('--autoupdate', type=float, metavar='SECONDS', help='automatically update index version and commit any changes')
parser.add_option('--autosync', metavar='HOST[:PORT][/PATH],...', help='automatically synchronize searcher with remote hosts and update')
parser.add_option('--real-time', action='store_true', help='search in real-time without committing')

if __name__ == '__main__':
    options, args = parser.parse_args()
    read_only = options.read_only or options.autosync or len(args) > 1
    kwargs = {'nrt': True} if options.real_time else {}
    if read_only and (options.real_time or not args):
        parser.error('incompatible read/write options')
    if options.autosync:
        kwargs['hosts'] = options.autosync.split(',')
        if not (options.autoupdate and len(args) == 1):
            parser.error('autosync requires autoupdate and a single directory')
    if options.config and not os.path.exists(options.config):
        options.config = {'global': json.loads(options.config)}
    cls = WebSearcher if read_only else WebIndexer
    root = cls.new(*map(os.path.abspath, args), **kwargs)
    del options.read_only, options.autosync, options.real_time
    start(root, callback=init, **options.__dict__)
