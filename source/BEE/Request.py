from urllib.parse import parse_qs
import json


########################### Exceptions

# Raised when request.body exceeds MAX_BODY_SIZE.
class BEE_ERROR_request_payload_too_large(Exception): pass



class Request:
	########################### Object

	########### APIs

	def __init__(self, environ, MAX_BODY_SIZE=None):
		self.environ = environ
		self.MAX_BODY_SIZE = MAX_BODY_SIZE
		self.body = None
		self.JSON = None
		self.headers = None

	# The URL path (``/user/42``).
	def get_path(self): return self.environ.get("PATH_INFO", "/")

	# Upper‑case HTTP verb (``GET``, ``POST``, …).
	def get_method(self): return self.environ.get("REQUEST_METHOD", "GET").upper()

	#### NOTE:
	# Query string: The part of the URL after the '?'
	# Query parameters or URL query parameters: The key-value pairs in the query string (e.g., ?page=2&sort=asc)
	def get_query_string(self): return parse_qs(self.environ.get("QUERY_STRING", ""), keep_blank_values=True)

	# Case‑title‑cased header mapping {"Content-Type": "…"}.
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
		if self.body is not None: return self.body

		try: length = int(self.environ.get("CONTENT_LENGTH") or 0)
		except (TypeError, ValueError): length = 0

		method = self.environ.get("REQUEST_METHOD", "GET").upper()
		stream = self.environ["wsgi.input"]

		#### Known size
		if length:
			if (
				self.MAX_BODY_SIZE is not None and
				length > self.MAX_BODY_SIZE
			): raise BEE_ERROR_request_payload_too_large()

			self.body = stream.read(length)

			return self.body

		##### No Content-Length
		# RFC 7231: GET, HEAD, DELETE, CONNECT, OPTIONS, TRACE normally have no body.
		if method in ("GET", "HEAD", "DELETE", "OPTIONS", "TRACE", "CONNECT"):
			self.body = b""
			return self.body

		# ‘chunked’ uploads.  Best to reject it early:
		raise BEE_ERROR_request_payload_too_large("Refusing to read an unknown-length request body")

	# Parse body as JSON once and memoize result.
	def get_JSON(self):
		if self.JSON is None:
			try: self.JSON = json.loads(self.get_body().decode() or "null")
			except json.JSONDecodeError: self.JSON = None

		return self.JSON

	########### Helpers
