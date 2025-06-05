from urllib.parse import parse_qs
import json

class Request:
	########################### Object

	########### APIs

	def __init__(self, environ):
		self.environ = environ
		self.body = None
		self.JSON = None
		self.headers = None

	# The URL path (``/user/42``).
	def get_path(self): return self.environ.get("PATH_INFO", "/")

	# Upper‑case HTTP verb (``GET``, ``POST``, …).
	def get_method(self): return self.environ.get("REQUEST_METHOD", "GET").upper()

	# Dict[str, List[str]] of query‑string params (``?a=1&a=2``).
	def get_query(self): return parse_qs(self.environ.get("QUERY_STRING", ""), keep_blank_values=True)

	# alias for convenience (Flask uses ``request.args``)
	get_args = get_query

	# Case‑title‑cased header mapping (``{"Content-Type": "…"}``).
	def get_headers(self):
		if self.headers is None:
			headers = {}

			for k, v in self.environ.items():
				if k.startswith("HTTP_"):
					name = k[5:].replace("_", "-").title()
					headers[name] = v

			for k in ("CONTENT_TYPE", "CONTENT_LENGTH"):
				if k in self.environ:
					name = k.replace("_", "-").title()
					headers[name] = self.environ[k]

			self.headers = headers

		return self.headers

	# Raw request body *bytes* (read once then cached).
	def get_body(self):
		if self.body is None:
			try: length = int(self.environ.get("CONTENT_LENGTH", 0) or 0)
			except ValueError: length = 0

			self.body = self.environ["wsgi.input"].read(length)

		return self.body

	# Parse body as JSON once and memoize result.
	def get_JSON(self):
		if self.JSON is None:
			try: self.JSON = json.loads(self.body().decode() or "null")
			except json.JSONDecodeError: self.JSON = None

		return self.JSON

	########### Helpers
