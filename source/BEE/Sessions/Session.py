import uuid

class Session(dict):
	########################### Object

	def __init__(self, data=None, new=True, sid=None):
		super().__init__(data or {})

		self.sid = sid or uuid.uuid4().hex

		# True if no valid cookie was sent
		self.new = new

		# flips to True on any mutation
		self.modified = False

	def __setitem__(self, key, value):
		self.modified = True
		super().__setitem__(key, value)

	def __delitem__(self, key):
		self.modified = True
		super().__delitem__(key)
