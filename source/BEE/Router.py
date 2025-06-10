import re

class Router:
	########################### Object

	########### APIs

	def __init__(self):
		# list of (method, compiled_regex, handler)
		self.routes = []

	def register_route(self, path_pattern, method, handler):
		regex = Router.__compile(path_pattern)
		self.routes.append((method.upper(), regex, handler))

	def add(self, path_pattern, method, handler):
		self.register_route(path_pattern, method, handler)

	# Return (handler, params_dict) or (None, None) if no match.
	def match(self, path, method):
		for m, regex, handler in self.routes:
			if m != method.upper(): continue

			match = regex.match(path)

			if match: return handler, match.groupdict()

		return None, None

	########################### Static

	param_re = re.compile(r"<([a-zA-Z_][a-zA-Z0-9_]*)>")

	########### Helpers

	# Translate ``/user/<name>`` → ``^/user/(?P<name>[^/]+)$`` and compile.
	@staticmethod
	def __compile(pattern):
		def repl(match):
			name = match.group(1)
			return fr"(?P<{name}>[^/]+)"

		regex_pattern = Router.param_re.sub(repl, pattern)
		regex_pattern = f"^{regex_pattern}$"
		return re.compile(regex_pattern)
