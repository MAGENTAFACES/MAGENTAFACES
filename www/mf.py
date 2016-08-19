import os
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from random import random
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware

class MagentaFaces(object):
	def __init__(self):
		path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jenv = Environment(loader=FileSystemLoader(path), autoescape=False)

		self.url_map = Map([Rule('/', endpoint='mf')])

	def mf(self, request, **context):
		path = os.path.join(os.path.dirname(__file__), 'prose')
		hlist = []
		for x in range(0,15):
			h = "h%04d.md" % x
			hlist.append(h)
		f = open(os.path.join(path, hlist[int(random() * (len(hlist)))]), 'r')
		try:
			head = unicode(f.read(), 'utf-8')
		finally:
			f.close()

		blam = ['diz', 'daz', 'dux']
		html = blam[int(random() * 3)] + '.html'

		prlist = []
		for x in range(0,31):
			p = "p%04d.md" % x
			prlist.append(p)

		f = open(os.path.join(path, prlist[int(random() * len(prlist))]), 'r')
		try:
			data = unicode(f.read(), 'utf-8')
		finally:
			f.close()
		prose = markdown(data)
		return self.render_template(html, head=head, prose=prose)

	def render_template(self, template_name, **context):
		t = self.jenv.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	def dispatch(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try: 
			endpoint, values = adapter.match()
			return getattr(self, endpoint)(request, **values)
		except NotFound, e:
			return self.render_template("daz.html", head="these faces are magenta", prose='and so are we')
		except HTTPException, e:
			return e

	def wsgi_app(self, environ, start_response):
	
		request = Request(environ)
		response = self.dispatch(request)
		return response(environ, start_response)

	def __call__(self, environ, start_response):
		return self.wsgi_app(environ, start_response)

def make_app(with_static=True):
	app = MagentaFaces()
	if with_static:
		app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
			'/static': os.path.join(os.path.dirname(__file__), 'static')
		})
	return app

if __name__ == '__main__':
	from werkzeug.serving import run_simple
	app = make_app()
	run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
