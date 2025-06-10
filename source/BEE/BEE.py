from wsgiref.simple_server import make_server

from .Router import Router
from .Request import Request, BEE_ERROR_request_payload_too_large
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

	def __call__(self, environ, start_response):
		request = Request(environ, self.MAX_BODY_SIZE)
		session = self.session_manager.load(environ)
		token = Session_Proxy.bind(session)
		response = None

		try:
			route_handler_func, params = self.router.match(request.get_path(), request.get_method())

			if route_handler_func is None:
				response = Response(
					b"Not Found",
					"404 NOT FOUND",
					[("Content-Type", "text/plain")]
				)

			else:
				# Handler may declare signature (request, **params) or (**params)
				try: return_value = route_handler_func(request, **params)
				except TypeError: return_value = route_handler_func(**params)

				if return_value is None:
					response = Response(
						b"No Response",
						"444 NO RESPONSE",
						[("Content-Type", "text/plain; charset=utf-8")]
					)

				else:
					response = Response(
						return_value,
						"200 OK",
						[("Content-Type", "text/plain")]
					)

			# Persist session if needed
			self.session_manager.save(session, response)

		except BEE_ERROR_request_payload_too_large:
			response = Response(
				b"Request entity too large",
				"413 REQUEST ENTITY TOO LARGE",
				[("Content-Type", "text/plain")]
			)

		finally: Session_Proxy.unbind(token)

		return response(start_response)

	def run(self, host="127.0.0.1", port=8000):
		with make_server(host, port, self) as server:
			print(f"BEE running on http://{host}:{port}")
			server.serve_forever()

	def route(self, path, methods=("GET",)):
		def decorator(func):
			for method in methods: self.router.register_route(path, method.upper(), func)
			return func

		return decorator
