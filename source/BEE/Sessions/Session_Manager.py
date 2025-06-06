import hmac, hashlib, base64, time

from BEE.Session import Session

class Session_Manager:
	########################### Static

	COOKIE_NAME = "BEE_session"

	# 1 week in seconds
	MAX_AGE = 60 * 60 * 24 * 7

	########################### Object

	########### APIs

	def __init__(self, secret: str):
		self.secret = secret

		# in‑memory: sid → (expires_epoch, data_dict)
		self.sessions = {}

	# Return a class "Session" extracted from the Cookie header.
	def load(self, environ):
		raw = environ.get("HTTP_COOKIE", "")

		sid = None

		for part in raw.split(";"):
			if "=" not in part: continue

			k, v = (p.strip() for p in part.split("=", 1))

			if k == Session_Manager.COOKIE_NAME:
				sid = self.__verify(v)
				break

		if not sid or sid not in self.sessions: return Session()

		expires, data = self.sessions[sid]

		# Expired in store (self.sessions)
		if expires < time.time():
			self.sessions.pop(sid, None)
			return Session()

		return Session(data=data, new=False, sid=sid)

	# Persist *session* and attach Set‑Cookie header if needed.
	def save(self, session: Session, response):
		if not (session.new or session.modified): return

		# persist to in‑memory store
		expires = int(time.time()) + Session_Manager.MAX_AGE
		self.sessions[session.sid] = (expires, dict(session))

		cookie_value = f"{session.sid}.{self.__sign(session.sid)}"

		head_value = (
			f"{Session_Manager.COOKIE_NAME}={cookie_value}; Path=/; HttpOnly; "
			f"Max-Age={Session_Manager.MAX_AGE}"
		)

		response.headers.append(("Set-Cookie", head_value))

	########### Helpers

	# Return URL‑safe base64 HMAC(signature) for *sid*.
	def __sign(self, sid: str):
		sig = hmac.new(self.secret.encode(), sid.encode(), hashlib.sha256).digest()
		return base64.urlsafe_b64encode(sig).decode().rstrip("=")

	# Return sid if signature is valid, else None
	def __verify(self, cookie_value: str):
		try:
			sid, sig = cookie_value.split(".", 1)
			return sid if hmac.compare_digest(self.__sign(sid), sig) else None

		except ValueError: return None
