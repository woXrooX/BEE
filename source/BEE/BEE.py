from wsgiref.simple_server import make_server

from BEE.Request import Request
from BEE.Response import Response
from BEE.Router import Router

class BEE:
	"""Back‑End Engine core object (WSGI‑callable + route registry)."""

	def __init__(self):
		self.router = Router()

	def route(self, path: str, methods=("GET",)):
		def decorator(func):
			for m in methods: self.router.add(path, m.upper(), func)
			return func

		return decorator

	def __call__(self, environ, start_response):
		req = Request(environ)

		handler, params = self.router.match(req.get_path(), req.get_method())

		if handler is None: return Response.not_found()(start_response)

		# Handler may declare signature (req, **params) or (**params)
		try: result = handler(req, **params)
		except TypeError: result = handler(**params)

		if isinstance(result, Response): return result(start_response)

		if isinstance(result, tuple): status, headers, body = result

		else:
			status = "200 OK"
			headers = [("Content-Type", "text/plain")]
			body = result

		return Response.generate_start_response(start_response, status, headers, body)

	def run(self, host="127.0.0.1", port=8000):
		with make_server(host, port, self) as server:
			print(f"BEE running on http://{host}:{port}")
			server.serve_forever()
