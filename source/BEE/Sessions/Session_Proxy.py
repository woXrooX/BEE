from contextvars import ContextVar
from BEE.Sessions.Session import Session

__BEE_current_session = ContextVar("__BEE_current_session", default=None)

class __Session_Proxy:
	########################### Static

	########### Helpers

	@staticmethod
	def __get():
		__SP_session = __BEE_current_session.get()
		if __SP_session is None: raise RuntimeError("No active request context; 'session' unavailable")
		return __SP_session


	########################### Object

	########### APIs

	def __getitem__(self, key): return __Session_Proxy.__get()[key]

	def __setitem__(self, key, val): __Session_Proxy.__get()[key] = val

	def __delitem__(self, key): del __Session_Proxy.__get()[key]

	def __iter__(self): return iter(__Session_Proxy.__get())

	def get(self, k, d=None): return __Session_Proxy.__get().get(k, d)

	def __getattr__(self, name): return getattr(__Session_Proxy.__get(), name)

	def __setattr__(self, name, val):
		if name.startswith("_"): object.__setattr__(self, name, val)
		else: setattr(__Session_Proxy.__get(), name, val)

	def __repr__(self): return f"<session proxy {__Session_Proxy.__get()!r}>"

session = __Session_Proxy()

# Bind *session* to the current context; return token for later reset.
def bind(session: Session): return __BEE_current_session.set(session)

# Reset the context to its previous state using *token*.
def unbind(token): __BEE_current_session.reset(token)
