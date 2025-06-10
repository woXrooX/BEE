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
		self.__store = {}

	def load(self, environ):
		sid = None

		for part in environ.get("HTTP_COOKIE", "").split(";"):
			if "=" not in part: continue

			key, value = (p.strip() for p in part.split("=", 1))

			if key == Session_Manager.COOKIE_NAME:
				sid = self.__verify(value)
				break

		if not sid: return Session_Object()

		with THREADING_LOCK: entry = self.__store.get(sid)

		if entry is None: return Session_Object()

		expires, data = entry

		if expires < time.time():
			with THREADING_LOCK: self.__store.pop(sid, None)
			return Session_Object()

		return Session_Object(data=data, new=False, sid=sid)

	def save(self, session, response):
		if not (session.new or session.modified): return

		expires = int(time.time()) + Session_Manager.MAX_AGE
		payload = dict(session)

		with THREADING_LOCK:
			self.__store[session.sid] = (expires, payload)

			now = time.time()

			for key, (exp, _) in list(self.__store.items()):
				if exp < now: self.__store.pop(key, None)

		cookie_value = f"{session.sid}.{self.__sign(session.sid)}"

		head_values   = (
			f"{Session_Manager.COOKIE_NAME}={cookie_value}; Path=/; HttpOnly; "
			f"Max-Age={Session_Manager.MAX_AGE}; SameSite=Lax; Secure"
		)

		response.headers.append(("Set-Cookie", head_values))

	########### Helpers
	def __sign(self, sid):
		raw = hmac.new(self.SECRET_KEY.encode(), sid.encode(), hashlib.sha256).digest()
		return base64.urlsafe_b64encode(raw).decode().rstrip("=")

	def __verify(self, cookie_value):
		try:
			sid, sig = cookie_value.split(".", 1)
			return sid if hmac.compare_digest(self.__sign(sid), sig) else None

		except ValueError: return None
