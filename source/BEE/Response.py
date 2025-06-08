class Response:
	########################### Object

	########### APIs

	def __init__(self, body=b'', status="200 OK", headers=None):
		self.body = body
		self.status = status
		self.headers = headers

		self.__convert_body_to_bytes()
		self.__validate_headers()
		self.__handle_content_length()

	def __call__(self, start_response):
		start_response(self.status, self.headers)
		return [self.body]


	########### Helpers
	# Normalise body into bytes.
	def __convert_body_to_bytes(self):
		if isinstance(self.body, bytes): pass

		elif isinstance(self.body, str): self.body = self.body.encode()

		# iterable / generator already producing bytes
		else: self.body = None


	def __validate_headers(self):
		if self.headers is None: self.headers = [("Content-Type", "text/plain")]
		else: self.headers = list(self.headers)

	# Accepts body type bytes
	def __handle_content_length(self):
		 # Streaming → let the app handle length itself
		if self.body is None: return

		content_length = str(len(self.body))

		# ensure exactly one Content-Length header with correct value
		for i, (k, v) in enumerate(self.headers):
			if k.lower() == "content-length":
				self.headers[i] = (k, content_length)
				break

		else: self.headers.append(("Content-Length", content_length))


	########################### Static

	########### APIs

	@staticmethod
	def generate_start_response(start_response, status, headers, body):
		if isinstance(body, str): body = body.encode()
		return Response(body, status, headers)(start_response)

	@staticmethod
	def ok(body=b"OK", headers=None):
		return Response(body, "200 OK", headers)

	@staticmethod
	def not_found(body=b"Not found"):
		return Response(body, "404 NOT FOUND", [("Content-Type", "text/plain")])

	@staticmethod
	def JSON(data, status="200 OK"):
		import json
		return Response(
			json.dumps(data),
			status,
			[("Content-Type", "application/json; charset=utf-8")]
		)

	########### Helpers go below
