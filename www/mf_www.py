import os
from jinja2 import Environment, FileSystemLoader
from markdown import markdown
from mf_common import get_prose, __NUM_HEADS__, __NUM_PROSE__
from random import random
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware

def make_app(with_static=True):
	app = MagentaFaces()
	if with_static:
		app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
			'/static': os.path.join(os.path.dirname(__file__), 'static')
		})
	return app

class MagentaFaces(object):
	def __init__(self):
		#setup jinja2 environment
		path = os.path.join(os.path.dirname(__file__), 'templates')
		self.jenv = Environment(loader=FileSystemLoader(path), autoescape=False)
		#map requests to /
		self.url_map = Map([Rule('/', endpoint='mf')])

	def mf(self, request, **context):
		#generate random header
		h = "h%04d.md" % int(random() * __NUM_HEADS__)	
		head = get_prose(h)

		#generate random html template
		blam = ['diz', 'daz', 'dux']
		html = blam[int(random() * 3)] + '.html'

		#generate random paragraph, rendered in markdown
		p = "p%04d.md" % int(random() * __NUM_HEADS__)
		data = get_prose(p)
		prose = markdown(data)
		#spurt propaganda
		return self.render_template(html, head=head, prose=prose)

	def render_template(self, template_name, **context):
		t = self.jenv.get_template(template_name)
		return Response(t.render(context), mimetype='text/html')

	def dispatch(self, request):
		adapter = self.url_map.bind_to_environ(request.environ)
		try: 
			endpoint, values = adapter.match()
			return getattr(self, endpoint)(request, **values)
		#return a placeholder to any non-/ request
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

#dev-mode
if __name__ == '__main__':
	from werkzeug.serving import run_simple
	app = make_app()
	run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)
