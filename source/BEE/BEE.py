from wsgiref.simple_server import make_server

from .Router import Router
from .Request import Request
from .Response import Response
from .Session.Session_Manager import Session_Manager
from .Session.Session_Proxy import Session_Proxy

class BEE:
	# Back‑End Engine core object (WSGI‑callable + route registry).
	def __init__(
		self,
		SECRET_KEY="BEE_dev",
		SQLite_DB_PATH = None,

		# 1 MB default
		MAX_BODY_SIZE = 1 << 20
	):
		self.router = Router()
		self.session_manager = Session_Manager(SECRET_KEY, SQLite_DB_PATH)
		self.MAX_BODY_SIZE = MAX_BODY_SIZE

	def route(self, path: str, methods=("GET",)):
		def decorator(func):
			for m in methods: self.router.register_route(path, m.upper(), func)
			return func

		return decorator

	def __call__(self, environ, start_response):
		request = Request(environ, self.MAX_BODY_SIZE)
		session = self.session_manager.load(environ)
		token = Session_Proxy.bind(session)

		try:
			handler, params = self.router.match(request.get_path(), request.get_method())
			if handler is None: response = Response.not_found()
			else:
				# Handler may declare signature (request, **params) or (**params)
				try: result = handler(request, **params)
				except TypeError: result = handler(**params)

				# Normalize result into Response
				if isinstance(result, Response): response = result

				elif isinstance(result, tuple):
					status, headers, body = result
					response = Response(body, status, headers)

				else: response = Response.ok(result)

			# Persist session if needed
			self.session_manager.save(session, response)

			return response(start_response)

		except RequestPayloadTooLarge:
			response = Response(
				b"Request entity too large",
				"413 REQUEST ENTITY TOO LARGE",
				[("Content-Type", "text/plain")]
			)

		finally: Session_Proxy.unbind(token)

		return Response.generate_start_response(start_response, status, headers, body)

	def run(self, host="127.0.0.1", port=8000):
		with make_server(host, port, self) as server:
			print(f"BEE running on http://{host}:{port}")
			server.serve_forever()
