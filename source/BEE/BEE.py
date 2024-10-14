if __name__ != "__main__":
	import re
	import inspect
	from functools import wraps

	from python.libs.BEE.Request import Request

	class BEE:
		#### Defaults

		def __init__(self):

			self.routes = {}
			# {
			# 	"compiled_path_pattern" : {
			# 		"handler_func": handler_func,
			# 		"URL_params": URL_params,
			# 		"methods": ["GET", "POST"]
			# 	}
			# }

		def __call__(self, environ, start_response):
			request = Request(environ)

			if request.method not in ["GET", "POST"]:
				start_response('405 Method Not Allowed', [('Content-Type', 'text/plain')])
				return [b'405 Method Not Allowed']

			for route_key, route_val in self.routes.items():
				match = route_key.match(request.path)

				if match:
					if request.method in route_val["methods"]:
						if request.method == "GET":
							kwargs = dict(zip(route_val["URL_params"], match.groups()))
							start_response('200 OK', [('Content-Type', 'text/html')])
							return [route_val["handler_func"](request=request, **kwargs).encode()]

						elif request.method == "POST":
							pass
							# POST resp

			start_response('404 Not Found', [('Content-Type', 'text/plain')])
			return [b'404 Not Found']




		#### Decorators

		def route(self, path_pattern, methods=["GET"]):
			def decorator(func):
				compiled_pattern, URL_params = self.compile_route_path_pattern(path_pattern)

				@wraps(func)
				def wrapper(request=None, **kwargs):
					sig = inspect.signature(func)
					if "request" in sig.parameters: return func(request, **kwargs)
					else: return func(**kwargs)

				self.routes[compiled_pattern] = {
					"handler_func": wrapper,
					"URL_params": URL_params,
					"methods": methods
				}

				return wrapper
			return decorator




		#### Helpers

		def compile_route_path_pattern(self, path):
			param_pattern = r'<([^>]+)>'
			URL_params = re.findall(param_pattern, path)
			regex_pattern = re.sub(param_pattern, r'([^/]+)', path)
			return re.compile(f"^{regex_pattern}$"), URL_params

