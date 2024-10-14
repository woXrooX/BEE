from urllib.parse import parse_qs
from http.cookies import SimpleCookie

class Request:
	def __init__(self, environ):
		self.environ = environ
		self.method = environ.get("REQUEST_METHOD", '')
		self.path = environ.get("PATH_INFO", '')
		self.query_string = environ.get("QUERY_STRING", '')
		self.content_type = environ.get("CONTENT_TYPE", '')
		self.content_length = int(environ.get("CONTENT_LENGTH", 0))

	def get_headers(self):
		return {key[5:]: value for key, value in self.environ.items() if key.startswith('HTTP_')}

	def get_body(self):
		content_length = self.content_length
		if content_length:
			return self.environ['wsgi.input'].read(content_length)
		return b''

	def get_query_params(self):
		return parse_qs(self.query_string)

	def get_form_data(self):
		if self.content_type == 'application/x-www-form-urlencoded':
			return parse_qs(self.get_body().decode('utf-8'))
		return {}

	def get_json(self):
		if self.content_type == 'application/json':
			import json
			return json.loads(self.get_body().decode('utf-8'))
		return None

	def get_cookies(self):
		cookie = SimpleCookie()
		cookie.load(self.environ.get('HTTP_COOKIE', ''))
		return {key: morsel.value for key, morsel in cookie.items()}

