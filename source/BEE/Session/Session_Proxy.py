from contextvars import ContextVar
from .Session_Object import Session_Object

CURRENT_SESSION = ContextVar("BEE_CURRENT_SESSION", default=None)

class Session_Proxy:
	########################### Static

	# Bind session to the current context; return token for later reset.
	@staticmethod
	def bind(session: Session_Object): return CURRENT_SESSION.set(session)

	# Reset the context to its previous state using token.
	@staticmethod
	def unbind(token): CURRENT_SESSION.reset(token)

	########### Helpers

	@staticmethod
	def __get():
		__SP_session = CURRENT_SESSION.get()
		if __SP_session is None: raise RuntimeError("No active request context; 'session' unavailable")
		return __SP_session


	########################### Object

	########### APIs

	def __getitem__(self, key): return Session_Proxy.__get()[key]

	def __setitem__(self, key, val): Session_Proxy.__get()[key] = val

	def __delitem__(self, key): del Session_Proxy.__get()[key]

	def __iter__(self): return iter(Session_Proxy.__get())

	def get(self, k, d=None): return Session_Proxy.__get().get(k, d)

	def __getattr__(self, name): return getattr(Session_Proxy.__get(), name)

	def __setattr__(self, name, val):
		if name.startswith("_"): object.__setattr__(self, name, val)
		else: setattr(Session_Proxy.__get(), name, val)

	def __repr__(self): return f"<BEE_session proxy {Session_Proxy.__get()!r}>"

session = Session_Proxy()
