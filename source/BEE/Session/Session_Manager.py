import hmac, hashlib, base64, json, time, threading, sqlite3, os, sys

from .Sessions import Sessions

# SQLite path
BASE_DIR = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "sessions.sqlite3")

THREADING_LOCK = threading.Lock()

class Session_Manager:
	########################### Static

	COOKIE_NAME = "BEE_COOKIE_SESSION"

	# 1 week in seconds
	MAX_AGE = 60 * 60 * 24 * 7

	########################### Object

	########### APIs

	def __init__(self, SECRET_KEY: str, SQLite_DB_PATH: str):
		self.SECRET_KEY = SECRET_KEY
		self.SQLite_DB_PATH = SQLite_DB_PATH or DEFAULT_DB_PATH

		self.db = sqlite3.connect(
			self.SQLite_DB_PATH,
			check_same_thread=False,
			isolation_level=None
		)

		self.__SQLite_init_session_schema()

	# Return a class "Sessions" extracted from the Cookie header.
	def load(self, environ):
		raw = environ.get("HTTP_COOKIE", "")
		sid = None

		for part in raw.split(";"):
			if "=" not in part: continue

			k, v = (p.strip() for p in part.split("=", 1))

			if k == Session_Manager.COOKIE_NAME:
				sid = self.__verify(v)
				break

		# no valid cookie → new session
		if not sid: return Sessions()

		with THREADING_LOCK: row = self.db.execute("SELECT expires, data FROM BEE_sessions WHERE sid=?;", (sid,)).fetchone()

		# No session in SQLite DB
		if row is None: return Sessions()

		expires, data_JSON = row

		# Expired. Purge & start fresh
		if expires < time.time():
			self.__SQLite_delete_session(sid)
			return Sessions()

		try: data = json.loads(data_JSON)
		except json.JSONDecodeError: data = {}

		return Sessions(data=data, new=False, sid=sid)

	# Persist session and attach Set‑Cookie header if needed.
	def save(self, session: Sessions, response):
		if not (session.new or session.modified): return

		expires = int(time.time()) + Session_Manager.MAX_AGE
		payload = json.dumps(dict(session))

		with THREADING_LOCK:
			self.db.execute("INSERT OR REPLACE INTO BEE_sessions(sid, expires, data) VALUES (?,?,?);", (session.sid, expires, payload),)

			# opportunistic GC
			self.db.execute("DELETE FROM BEE_sessions WHERE expires < ?;", (int(time.time()),),)

		cookie_value = f"{session.sid}.{self.__sign(session.sid)}"

		head_values = (
			f"{Session_Manager.COOKIE_NAME}={cookie_value}; Path=/; HttpOnly; "
			f"Max-Age={Session_Manager.MAX_AGE}; SameSite=Lax; Secure"
		)

		response.headers.append(("Set-Cookie", head_values))

	########### Helpers
	def __SQLite_init_session_schema(self):
		with THREADING_LOCK:
			self.db.execute("CREATE TABLE IF NOT EXISTS BEE_sessions (sid TEXT PRIMARY KEY, expires INTEGER, data TEXT);")
			self.db.execute("CREATE INDEX IF NOT EXISTS index_expires ON BEE_sessions(expires);")

	def __SQLite_delete_session(self, sid: str):
		with THREADING_LOCK: self.db.execute("DELETE FROM BEE_sessions WHERE sid=?;", (sid,))

	# Return URL‑safe base64 HMAC(signature) for sid.
	def __sign(self, sid: str):
		sig = hmac.new(self.SECRET_KEY.encode(), sid.encode(), hashlib.sha256).digest()
		return base64.urlsafe_b64encode(sig).decode().rstrip("=")

	# Return sid if signature is valid, else None
	def __verify(self, cookie_value: str):
		try:
			sid, sig = cookie_value.split(".", 1)
			return sid if hmac.compare_digest(self.__sign(sid), sig) else None

		except ValueError: return None
