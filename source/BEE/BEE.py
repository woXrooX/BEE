if __name__ != "__main__":
	import re

	class BEE:
		#### Defaults

		def __init__(self):
			self.routes = {}
			# {
			# 	"pattern" : {
			# 		"handler_func": handler_func,
			# 		"URL_params": URL_params
			# 	}
			# }

		def __call__(self, environ, start_response):
			environ_path = environ['PATH_INFO']

			for pattern, route_info in self.routes.items():

				match = pattern.match(environ_path)

				if match:
					kwargs = dict(zip(route_info["URL_params"], match.groups()))
					start_response('200 OK', [('Content-Type', 'text/html')])
					return [route_info["handler_func"](**kwargs).encode()]

			start_response('404 Not Found', [('Content-Type', 'text/plain')])
			return [b'404 Not Found']




		#### Decorators

		def route(self, path):
			def decorator(handler_func):
				pattern, URL_params = self.compile_route_path(path)

				self.routes[pattern] = {
					"handler_func": handler_func,
					"URL_params": URL_params
				}

				return handler_func

			return decorator




		#### Helpers

		def compile_route_path(self, path):
			param_pattern = r'<([^>]+)>'
			URL_params = re.findall(param_pattern, path)
			regex_pattern = re.sub(param_pattern, r'([^/]+)', path)
			return re.compile(f"^{regex_pattern}$"), URL_params

