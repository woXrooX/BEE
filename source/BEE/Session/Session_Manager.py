import hmac, hashlib, base64, json, time, threading

from .Session_Object import Session_Object

THREADING_LOCK = threading.Lock()

class Session_Manager:
	########################### Static

	COOKIE_NAME = "BEE_COOKIE_SESSION"

	# 1 week in seconds
	MAX_AGE = 60 * 60 * 24 * 7

	########################### Object

	########### APIs

	def __init__(self, SECRET_KEY):
		self.SECRET_KEY = SECRET_KEY

	# Return a class "Session_Object" extracted from the Cookie header.
	def load(self, environ):
		raw = environ.get("HTTP_COOKIE", "")
		sid = None

		for part in raw.split(";"):
			if "=" not in part: continue

			key, value = (p.strip() for p in part.split("=", 1))

			if key == Session_Manager.COOKIE_NAME:
				sid = self.__verify(value)
				break

		# no valid cookie → new session
		if not sid: return Session_Object()

		# For in-memory sessions, we don't need to check the database
		return Session_Object(new=False, sid=sid)

	# Persist session and attach Set‑Cookie header if needed.
	def save(self, session, response):
		if not (session.new or session.modified): return

		expires = int(time.time()) + Session_Manager.MAX_AGE

		cookie_value = f"{session.sid}.{self.__sign(session.sid)}"

		head_values = (
			f"{Session_Manager.COOKIE_NAME}={cookie_value}; Path=/; HttpOnly;"
			f"Max-Age={Session_Manager.MAX_AGE}; SameSite=Lax; Secure"
		)

		response.headers.append(("Set-Cookie", head_values))

	########### Helpers

	# Return URL‑safe base64 HMAC(signature) for sid.
	def __sign(self, sid):
		sig = hmac.new(self.SECRET_KEY.encode(), sid.encode(), hashlib.sha256).digest()
		return base64.urlsafe_b64encode(sig).decode().rstrip("=")

	# Return sid if signature is valid, else None
	def __verify(self, cookie_value):
		try:
			sid, sig = cookie_value.split(".", 1)
			return sid if hmac.compare_digest(self.__sign(sid), sig) else None

		except ValueError: return None
