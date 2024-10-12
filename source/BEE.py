# BEE = Back-End Engine

if __name__ != "__main__":
	import re

	class Route:
		def __init__(self, pattern, handler):
			self.pattern = pattern
			self.handler = handler

	class BEE:
		def __init__(self):
			self.routes = []

		def route(self, path):
			def decorator(handler):
				pattern = re.compile(f"^{path}$")
				self.routes.append(Route(pattern, handler))
				return handler
			return decorator

		def __call__(self, environ, start_response):
			path = environ['PATH_INFO']
			for route in self.routes:
				match = route.pattern.match(path)
				if match:
					response = route.handler()
					start_response('200 OK', [('Content-Type', 'text/html')])
					return [response.encode()]

			start_response('404 Not Found', [('Content-Type', 'text/plain')])
			return [b'404 Not Found']
