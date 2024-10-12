import re

class BEE:
	def __init__(self):
		# "path": "handler_func"
		self.routes = {}

	def __call__(self, environ, start_response):
		environ_path = environ['PATH_INFO']

		for path, handler_func in self.routes.items():
			match = path.match(environ_path)

			if match:
				start_response('200 OK', [('Content-Type', 'text/html')])
				return [handler_func().encode()]

			start_response('404 Not Found', [('Content-Type', 'text/plain')])
			return [b'404 Not Found']

	def route(self, path):
		def decorator(handler_func):
			self.routes[re.compile(f"^{path}$")] = handler_func
			return handler_func

		return decorator
