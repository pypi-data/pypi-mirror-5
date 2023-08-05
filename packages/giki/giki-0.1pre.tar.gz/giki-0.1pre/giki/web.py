from .core import PageNotFound
from .formatter import format, get_names
from jinja2 import Environment, PackageLoader
from StringIO import StringIO
from traceback import print_exc

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.utils import redirect
from werkzeug.exceptions import HTTPException, NotFound

t = Environment(loader=PackageLoader('giki', 'templates'))

class WebWiki (object):
	debug = False

	def __init__(self, wiki):
		self.wiki = wiki

		# construct routing map
		self.url_map = Map([
			Rule('/', endpoint='home'),
			Rule('/<path:path>', endpoint='show_page'),
			Rule('/+create', endpoint='create_page'),
		])

	# WSGI stuff

	def dispatch_request(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try:
			endpoint, values = adapter.match()
			return getattr(self, endpoint)(request, **values)
		except NotFound as e:
			return self.handle_not_found(request)
		except HTTPException, e:
			return e

	def wsgi_app(self, environ, start_response):
		request = Request(environ)
		response = self.dispatch_request(request)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)

	def serve(self, port=8080):
		from werkzeug.serving import run_simple
		run_simple('127.0.0.1', port, self, use_debugger=self.debug, use_reloader=self.debug)

	# Authentication stuff

	def get_permission(self, request, type):
		"""Override this to implement permissions.

		@param type 'read' or 'write' as appropriate.
		@return the appropriate Git author string."""
		return 'Example Exampleson <example@example.com>'

	# Actual application stuff

	def home(self, request):
		return redirect('/index')

	def show_page(self, request, path):
		if request.method == 'GET':
			self.get_permission(request, 'read')
			try:
				p = self.wiki.get_page(path)
			except PageNotFound:
				raise NotFound()
			fmt_human, fmt_cm = get_names(p)

			# get path components for breadcrumb
			split_path = path.split('/')
			path_components = []
			if path != self.wiki.default_page:
				for i, cpt in enumerate(split_path):
					out_cpt = {
					'name': cpt,
					'path': '/'.join(split_path[:i])
					}
					path_components.append(out_cpt)

			attrs = {
				'page': p,
				'content': format(p),
				'fmt_human': fmt_human,
				'fmt_cm': fmt_cm,
				'path_components': path_components,
				'default_page': self.wiki.default_page,
			}
			return Response(t.get_template('page.html').render(**attrs), mimetype='text/html')
		elif request.method == 'POST':
			author = self.get_permission(request, 'write')
			p = self.wiki.get_page_at_commit(path, request.form['commit_id'])
			p.content = request.form['content']
			p.save(author, request.form['commit_msg'])
			return redirect('/' + path)

	def __repr__(self):
		return super(WebWiki, self).__repr__()

	def create_page(self, request):
		author = self.get_permission(request, 'write')
		p = self.wiki.create_page(request.form['path'], 'mdown', author)
		return redirect('/' + request.form['path'])

	def handle_not_found(self, request):
		r = Response(t.get_template('404.html').render(request=request), mimetype='text/html')
		r.status_code = 404
		return r

	def handle_internal_error(self, request, exc):
		io = StringIO()
		print_exc(file=io)
		return Response(t.get_template('500.html').render(request=request, traceback=io.getvalue()))

class SingleUserWiki (WebWiki):
	def __init__(self, wiki, author):
		WebWiki.__init__(self, wiki)
		self.author = author

	def get_permission(self, request, type):
		return self.author
