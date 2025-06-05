class Response:
	########################### Object

	########### APIs

	def __init__(self, body=b'', status="200 OK", headers=None):
		if isinstance(body, str): body = body.encode()

		content_length = str(len(body))

		if headers is None: headers = [("Content-Type", "text/plain")]
		else: headers = list(headers)

		# ensure exactly one Content-Length header with correct value
		for i, (k, v) in enumerate(headers):
			if k.lower() == "content-length":
				headers[i] = (k, content_length)
				break

		else: headers.append(("Content-Length", content_length))

		self.body = body
		self.status = status
		self.headers = headers

	def __call__(self, start_response):
		start_response(self.status, self.headers)
		return [self.body]


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
